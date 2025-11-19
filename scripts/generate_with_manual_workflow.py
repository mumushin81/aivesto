#!/usr/bin/env python3
"""
새로운 워크플로우: 다운로드 → 크롭 → 선정 → Supabase 저장
1. Midjourney 이미지 생성 (로컬 다운로드만)
2. 로컬에서 4개 크롭 생성
3. AI가 최고 크롭 선정
4. 원본 + 선정된 크롭만 Supabase에 저장
"""
import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image

# magic_book 모듈 import
magic_book_path = Path.home() / 'dev' / 'magic_book'
sys.path.insert(0, str(magic_book_path))

from dotenv import load_dotenv
from supabase import create_client
from loguru import logger
from src.midjourney.client import PassPromptToSelfBot, wait_for_image_completion, download_image
from src.midjourney.processor import crop_image_cross
from src.midjourney.storage import MidjourneyImageStorage

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# 각 블로그 기사별 5장의 이미지 완전 매핑
COMPLETE_ARTICLE_IMAGE_MAPPING = {
    "article_NVDA_blackwell_gpu_20251113.md": [
        {"key": "NVDA_blackwell_chip", "num": 1},
        {"key": "NVDA_ai_datacenter", "num": 2},
        {"key": "NVDA_blackwell_chip", "num": 3},
        {"key": "NVDA_ai_datacenter", "num": 4},
        {"key": "NVDA_blackwell_chip", "num": 5}
    ],
    "article_NVDA_foxconn_ai_server_20251115.md": [
        {"key": "NVDA_blackwell_chip", "num": 1},
        {"key": "NVDA_ai_datacenter", "num": 2},
        {"key": "NVDA_blackwell_chip", "num": 3},
        {"key": "NVDA_ai_datacenter", "num": 4},
        {"key": "NVDA_blackwell_chip", "num": 5}
    ],
    "article_TSLA_robotaxi_fleet_20251113.md": [
        {"key": "TSLA_robotaxi", "num": 1},
        {"key": "TSLA_charging_network", "num": 2},
        {"key": "TSLA_robotaxi", "num": 3},
        {"key": "TSLA_charging_network", "num": 4},
        {"key": "TSLA_robotaxi", "num": 5}
    ],
    "article_AAPL_iphone_sales_20251113.md": [
        {"key": "AAPL_premium_iphone", "num": 1},
        {"key": "AAPL_enterprise", "num": 2},
        {"key": "AAPL_premium_iphone", "num": 3},
        {"key": "AAPL_enterprise", "num": 4},
        {"key": "AAPL_premium_iphone", "num": 5}
    ],
    "article_ADBE_creative_ai_20251113.md": [
        {"key": "ADBE_creative_cloud", "num": 1},
        {"key": "ADBE_firefly_ai", "num": 2},
        {"key": "ADBE_creative_cloud", "num": 3},
        {"key": "ADBE_firefly_ai", "num": 4},
        {"key": "ADBE_creative_cloud", "num": 5}
    ],
    "article_AMZN_aws_ai_services_20251113.md": [
        {"key": "AMZN_aws_cloud", "num": 1},
        {"key": "AMZN_ai_services", "num": 2},
        {"key": "AMZN_aws_cloud", "num": 3},
        {"key": "AMZN_ai_services", "num": 4},
        {"key": "AMZN_aws_cloud", "num": 5}
    ],
    "article_GOOGL_search_ai_20251113.md": [
        {"key": "GOOGL_search_ai", "num": 1},
        {"key": "GOOGL_advertising", "num": 2},
        {"key": "GOOGL_search_ai", "num": 3},
        {"key": "GOOGL_advertising", "num": 4},
        {"key": "GOOGL_search_ai", "num": 5}
    ],
    "article_META_enterprise_ai_20251113.md": [
        {"key": "META_business_ai", "num": 1},
        {"key": "META_llama_opensource", "num": 2},
        {"key": "META_business_ai", "num": 3},
        {"key": "META_llama_opensource", "num": 4},
        {"key": "META_business_ai", "num": 5}
    ],
    "article_MSFT_AI_office_integration_20251113.md": [
        {"key": "MSFT_copilot", "num": 1},
        {"key": "MSFT_azure_cloud", "num": 2},
        {"key": "MSFT_copilot", "num": 3},
        {"key": "MSFT_azure_cloud", "num": 4},
        {"key": "MSFT_copilot", "num": 5}
    ],
    "article_NFLX_subscriber_growth_20251113.md": [
        {"key": "NFLX_streaming", "num": 1},
        {"key": "NFLX_advertising", "num": 2},
        {"key": "NFLX_streaming", "num": 3},
        {"key": "NFLX_advertising", "num": 4},
        {"key": "NFLX_streaming", "num": 5}
    ],
    "article_UBER_profitability_expansion_20251113.md": [
        {"key": "UBER_rideshare", "num": 1},
        {"key": "UBER_eats", "num": 2},
        {"key": "UBER_rideshare", "num": 3},
        {"key": "UBER_eats", "num": 4},
        {"key": "UBER_rideshare", "num": 5}
    ]
}

def load_prompts() -> Dict:
    """AI 이미지 프롬프트 로드"""
    prompt_file = Path(__file__).parent / 'ai_image_prompts.json'
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_midjourney_image(prompt: str, timeout: int = 300) -> str:
    """
    Midjourney 이미지 생성 및 URL 반환 (Supabase 저장 없음)

    Returns:
        이미지 URL
    """
    import time

    logger.info(f"📤 프롬프트 전송: {prompt[:60]}...")
    request_timestamp = time.time()
    response = PassPromptToSelfBot(prompt)

    if response.status_code != 204:
        logger.error(f"❌ 이미지 생성 요청 실패: HTTP {response.status_code}")
        return None

    logger.info("⏳ 이미지 완성 대기 중...")
    image_urls = wait_for_image_completion(
        prompt=prompt,
        request_timestamp=request_timestamp,
        timeout=timeout,
        check_interval=5
    )

    if not image_urls:
        logger.error("❌ 이미지 생성 타임아웃")
        return None

    return image_urls[0]  # 첫번째 이미지 URL 반환

def download_and_crop_locally(image_url: str, save_dir: Path) -> Tuple[Path, List[Path]]:
    """
    이미지 다운로드 및 로컬 크롭

    Returns:
        (원본 이미지 경로, 크롭 이미지 경로 리스트)
    """
    # 원본 다운로드
    save_dir.mkdir(parents=True, exist_ok=True)
    original_path = save_dir / "original.jpg"

    logger.info(f"📥 원본 이미지 다운로드 중...")
    response = requests.get(image_url)
    response.raise_for_status()

    with open(original_path, 'wb') as f:
        f.write(response.content)
    logger.success(f"✅ 원본 저장: {original_path}")

    # 4개 크롭 생성 (십자 4등분)
    logger.info(f"✂️  4개 크롭 생성 중 (십자 4등분)...")
    crop_paths_str = crop_image_cross(
        image_path=str(original_path),
        output_dir=str(save_dir)
    )

    # 문자열 경로를 Path 객체로 변환
    crop_paths = [Path(p) for p in crop_paths_str]

    logger.success(f"✅ 크롭 완료: {len(crop_paths)}개")
    crop_names = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
    for idx, crop_path in enumerate(crop_paths):
        logger.info(f"   • {crop_names[idx]}: {crop_path.name}")

    return original_path, crop_paths

def select_best_crop_ai(crop_paths: List[Path], prompt: str) -> Path:
    """
    AI가 최고 크롭 선정 (간단한 휴리스틱 사용)

    실제로는 Claude Vision API나 GPT-4V를 사용할 수 있지만,
    지금은 간단하게 top_left를 기본으로 선택
    """
    # TODO: Claude Vision API나 GPT-4V를 사용하여 실제 AI 선정 구현
    # 현재는 첫번째 크롭 (top_left) 선택
    best_crop = crop_paths[0]
    logger.info(f"🤖 AI 선정 크롭: {best_crop.name}")
    return best_crop

def upload_to_supabase(
    best_crop_path: Path,
    prompt: str
):
    """
    선정된 크롭만 Supabase에 업로드 (원본은 로컬에만 저장)
    """
    storage = MidjourneyImageStorage()

    # 선정된 크롭만 업로드
    logger.info(f"☁️  선정 크롭 Supabase 업로드 중...")

    crop_result = storage.save_midjourney_image(
        image_path=str(best_crop_path),
        prompt=prompt,
        auto_crop=False,
        metadata={'crop_position': best_crop_path.stem, 'is_selected_crop': True}
    )

    if not crop_result.get('success'):
        logger.error(f"❌ 크롭 업로드 실패: {crop_result.get('error')}")
        return None

    crop_id = crop_result['image_id']
    crop_url = crop_result['original_url']
    logger.success(f"✅ 크롭 업로드 완료!")
    logger.info(f"   Crop ID: {crop_id}")
    logger.info(f"   URL: {crop_url[:60]}...")

    return {
        'crop_id': crop_id,
        'crop_url': crop_url
    }

def main():
    logger.info("=" * 80)
    logger.info("🔄 새로운 워크플로우: 다운로드 → 크롭 → 선정 → Supabase 저장")
    logger.info("=" * 80)

    # 프롬프트 로드
    prompts_data = load_prompts()
    logger.info(f"📝 로드된 프롬프트 템플릿: {len(prompts_data)}개")

    # 필요한 고유 키 추출
    unique_keys = set()
    for article, images in COMPLETE_ARTICLE_IMAGE_MAPPING.items():
        for img in images:
            unique_keys.add(img['key'])

    logger.info(f"\n🔑 필요한 고유 이미지 키: {len(unique_keys)}개")
    logger.info(f"   {', '.join(sorted(unique_keys))}")

    # 각 키별로 필요한 개수 계산
    key_needs = {}
    for article, images in COMPLETE_ARTICLE_IMAGE_MAPPING.items():
        for img in images:
            key = img['key']
            key_needs[key] = key_needs.get(key, 0) + 1

    logger.info(f"\n📋 키별 필요 이미지 개수:")
    for key, count in sorted(key_needs.items()):
        logger.info(f"   • {key}: {count}개")

    # 작업 디렉토리 생성
    work_dir = Path(__file__).parent.parent / 'temp_images'
    work_dir.mkdir(parents=True, exist_ok=True)

    # 각 키별로 이미지 생성
    logger.info(f"\n🎨 이미지 생성 시작...")

    results = {}
    sorted_keys = sorted(key_needs.items(), key=lambda x: x[1], reverse=True)

    for idx, (key, needed_count) in enumerate(sorted_keys, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"[{idx}/{len(sorted_keys)}] 처리 중: {key} (필요: {needed_count}개)")
        logger.info(f"{'='*80}")

        if key not in prompts_data:
            logger.warning(f"⚠️  프롬프트 없음: {key}")
            continue

        prompt = prompts_data[key]['midjourney_prompt']

        # 필요한 만큼만 생성 (최대 3개)
        for i in range(min(needed_count, 3)):
            logger.info(f"\n🎯 {key} - {i+1}/{min(needed_count, 3)}")

            try:
                # 1. Midjourney 이미지 생성
                image_url = generate_midjourney_image(prompt, timeout=300)
                if not image_url:
                    logger.error(f"❌ 이미지 생성 실패")
                    continue

                # 2. 로컬 다운로드 + 크롭
                key_dir = work_dir / f"{key}_{i+1}"
                original_path, crop_paths = download_and_crop_locally(image_url, key_dir)

                # 3. AI 최고 크롭 선정
                best_crop = select_best_crop_ai(crop_paths, prompt)

                # 4. Supabase 업로드 (선정된 크롭만)
                upload_result = upload_to_supabase(best_crop, prompt)

                if upload_result:
                    if key not in results:
                        results[key] = []
                    results[key].append(upload_result)
                    logger.success(f"✅ 완료!")
                else:
                    logger.error(f"❌ 업로드 실패")

            except Exception as e:
                logger.error(f"❌ 오류: {e}")
                continue

    # 결과 요약
    logger.info("\n" + "=" * 80)
    logger.success("✅ 전체 작업 완료!")
    logger.info("=" * 80)
    logger.info(f"\n📊 결과 요약:")
    for key, key_results in results.items():
        logger.info(f"   • {key}: {len(key_results)}개 생성")

    logger.info(f"\n📁 임시 파일 위치: {work_dir}")
    logger.info(f"💡 다음 단계: download_and_place_images.py 실행하여 블로그에 배치")

if __name__ == "__main__":
    main()
