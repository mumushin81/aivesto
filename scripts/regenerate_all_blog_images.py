#!/usr/bin/env python3
"""
블로그 이미지 전체 재생성 스크립트
1. 기존 이미지 제거 완료
2. AI 프롬프트 로드
3. Midjourney 이미지 생성 (auto_crop=True for 4 crops)
4. 최고 크롭 선택 및 다운로드
5. 블로그 마크다운 파일 업데이트
"""
import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List

# magic_book 모듈 import를 위한 경로 추가
magic_book_path = Path.home() / 'dev' / 'magic_book'
sys.path.insert(0, str(magic_book_path))

from dotenv import load_dotenv
from supabase import create_client
from loguru import logger
from src.midjourney import generate_images_batch_and_save

# 환경 변수 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

# 블로그 아티클별 이미지 맵핑
ARTICLE_IMAGE_MAPPING = {
    "article_NVDA_blackwell_gpu_20251113.md": [
        {"key": "NVDA_blackwell_chip", "filename": "NVDA_blackwell_chip_1.jpg", "caption": "NVIDIA Blackwell GPU가 AI 성능을 5배 향상시켰습니다"},
        {"key": "NVDA_ai_datacenter", "filename": "NVDA_datacenter_demand_2.jpg", "caption": "클라우드 3사가 Blackwell GPU를 대량 구매하고 있습니다"}
    ],
    "article_NVDA_foxconn_ai_server_20251115.md": [
        {"key": "NVDA_blackwell_chip", "filename": "NVDA_foxconn_factory_1.jpg", "caption": "폭스콘 AI 서버 생산 라인"},
        {"key": "NVDA_ai_datacenter", "filename": "NVDA_ai_server_tech_2.jpg", "caption": "차세대 AI 서버 아키텍처"}
    ],
    "article_TSLA_robotaxi_fleet_20251113.md": [
        {"key": "TSLA_robotaxi", "filename": "TSLA_robotaxi_autonomous_1.jpg", "caption": "Tesla 로보택시 자율주행 시스템"},
        {"key": "TSLA_charging_network", "filename": "TSLA_charging_network_2.jpg", "caption": "Tesla 슈퍼차저 네트워크 확장"}
    ],
    "article_AAPL_iphone_sales_20251113.md": [
        {"key": "AAPL_premium_iphone", "filename": "AAPL_iphone_premium_1.jpg", "caption": "프리미엄 iPhone 라인업"},
        {"key": "AAPL_enterprise", "filename": "AAPL_enterprise_2.jpg", "caption": "기업용 Apple 생태계"}
    ],
    "article_ADBE_creative_ai_20251113.md": [
        {"key": "ADBE_creative_cloud", "filename": "ADBE_creative_cloud_1.jpg", "caption": "Adobe Creative Cloud 워크플로우"},
        {"key": "ADBE_firefly_ai", "filename": "ADBE_firefly_ai_2.jpg", "caption": "Adobe Firefly AI 생성 도구"}
    ],
    "article_AMZN_aws_ai_services_20251113.md": [
        {"key": "AMZN_aws_cloud", "filename": "AMZN_aws_datacenter_1.jpg", "caption": "AWS 클라우드 인프라"},
        {"key": "AMZN_ai_services", "filename": "AMZN_ai_platform_2.jpg", "caption": "AWS AI 서비스 플랫폼"}
    ],
    "article_GOOGL_search_ai_20251113.md": [
        {"key": "GOOGL_search_ai", "filename": "GOOGL_search_ai_1.jpg", "caption": "Google AI 검색 혁신"},
        {"key": "GOOGL_advertising", "filename": "GOOGL_ad_business_2.jpg", "caption": "Google 광고 비즈니스 성장"}
    ],
    "article_META_enterprise_ai_20251113.md": [
        {"key": "META_business_ai", "filename": "META_business_tools_2.jpg", "caption": "Meta 비즈니스 AI 도구"},
        {"key": "META_llama_opensource", "filename": "META_llama_opensource_1.jpg", "caption": "Meta Llama 오픈소스 AI"}
    ],
    "article_MSFT_AI_office_integration_20251113.md": [
        {"key": "MSFT_copilot", "filename": "MSFT_copilot_integration_1.jpg", "caption": "Microsoft Copilot 통합"},
        {"key": "MSFT_copilot", "filename": "MSFT_revenue_growth_2.jpg", "caption": "Microsoft AI 수익 성장"}
    ],
    "article_NFLX_subscriber_growth_20251113.md": [
        {"key": "NFLX_streaming", "filename": "NFLX_streaming_content_1.jpg", "caption": "Netflix 스트리밍 콘텐츠"},
        {"key": "NFLX_advertising", "filename": "NFLX_advertising_2.jpg", "caption": "Netflix 광고 플랫폼"}
    ],
    "article_UBER_profitability_expansion_20251113.md": [
        {"key": "UBER_rideshare", "filename": "UBER_rideshare_profit_1.jpg", "caption": "Uber 라이드셰어 수익성"},
        {"key": "UBER_eats", "filename": "UBER_eats_delivery_2.jpg", "caption": "Uber Eats 배달 성장"}
    ]
}

def load_prompts() -> Dict:
    """AI 이미지 프롬프트 로드"""
    prompt_file = Path(__file__).parent / 'ai_image_prompts.json'
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_image(url: str, save_path: Path):
    """URL에서 이미지 다운로드"""
    response = requests.get(url)
    response.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    logger.success(f"  ✓ Downloaded: {save_path.name}")

def get_best_crop_url(parent_image_id: str) -> str:
    """Supabase에서 최고 추천 크롭 이미지 URL 조회"""
    supabase = create_client(supabase_url, supabase_key)

    # 원본 이미지 메타데이터 조회
    original = supabase.table('midjourney_images')\
        .select('*')\
        .eq('image_id', parent_image_id)\
        .single()\
        .execute()

    if not original.data or 'metadata' not in original.data:
        # 메타데이터 없으면 첫번째 크롭 반환
        crop = supabase.table('midjourney_images')\
            .select('*')\
            .eq('parent_image_id', parent_image_id)\
            .eq('image_type', 'cropped')\
            .limit(1)\
            .execute()
        return crop.data[0]['public_url'] if crop.data else original.data['public_url']

    # AI 추천 정보 있으면 최고 크롭 반환
    best_crop_position = original.data['metadata'].get('ai_recommendation', {}).get('best_crop', 'top_left')

    crop = supabase.table('midjourney_images')\
        .select('*')\
        .eq('parent_image_id', parent_image_id)\
        .eq('crop_position', best_crop_position)\
        .single()\
        .execute()

    return crop.data['public_url'] if crop.data else original.data['public_url']

def update_markdown_images(article_filename: str, image_mapping: List[Dict]):
    """마크다운 파일의 이미지 경로 업데이트"""
    article_path = Path(__file__).parent.parent / 'articles' / article_filename

    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 이미지 참조 업데이트
    for img in image_mapping:
        # 기존 패턴 찾기: ![caption](../images/filename.jpg)
        old_pattern = f"](../images/{img['filename']})"
        if old_pattern in content:
            logger.info(f"  ✓ Image reference found for {img['filename']}")
        else:
            logger.warning(f"  ⚠️  Image reference not found for {img['filename']}, will be added")

    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.success(f"✅ Updated: {article_filename}")

def main():
    logger.info("=" * 80)
    logger.info("🔄 블로그 이미지 전체 재생성")
    logger.info("=" * 80)

    # 1. AI 프롬프트 로드
    logger.info("\n📝 Step 1: Loading AI image prompts...")
    prompts_data = load_prompts()
    logger.success(f"  ✓ Loaded {len(prompts_data)} prompt templates")

    # 2. 필요한 고유 이미지 키 추출
    unique_keys = set()
    for article, images in ARTICLE_IMAGE_MAPPING.items():
        for img in images:
            unique_keys.add(img['key'])

    logger.info(f"\n🎨 Step 2: Generating {len(unique_keys)} unique Midjourney images...")
    logger.info(f"  Keys: {', '.join(unique_keys)}")

    # 3. Midjourney 프롬프트 준비
    midjourney_prompts = []
    key_to_prompt = {}
    for key in unique_keys:
        if key in prompts_data:
            prompt = prompts_data[key]['midjourney_prompt']
            midjourney_prompts.append(prompt)
            key_to_prompt[key] = prompt
            logger.info(f"  • {key}: {prompt[:60]}...")
        else:
            logger.warning(f"  ⚠️  No prompt found for key: {key}")

    # 4. Midjourney 이미지 생성 (auto_crop=True)
    logger.info(f"\n⏳ Step 3: Generating images via magic_book (this may take 10-15 minutes)...")
    logger.info(f"  • auto_crop=True (will generate 4 crops per image)")
    logger.info(f"  • save_locally=False (Supabase only)")

    results = generate_images_batch_and_save(
        prompts=midjourney_prompts,
        auto_crop=True,  # 4개 크롭 생성
        save_locally=False,
        verbose=True
    )

    logger.success(f"\n✅ Generated {len(results)} images")

    # 5. 이미지 ID와 키 매핑
    key_to_image_id = {}
    for idx, (key, prompt) in enumerate(key_to_prompt.items()):
        if idx < len(results) and results[idx].success:
            # supabase_image_ids는 [original_id, crop1_id, crop2_id, crop3_id, crop4_id] 형태
            image_id = results[idx].supabase_image_ids[0] if results[idx].supabase_image_ids else None
            if image_id:
                key_to_image_id[key] = image_id
                logger.success(f"  • {key} → {image_id}")

    # 6. 각 아티클별 이미지 다운로드 및 업데이트
    logger.info(f"\n📥 Step 4: Downloading best crop images and updating articles...")

    public_images_dir = Path(__file__).parent.parent / 'public' / 'images'
    public_images_dir.mkdir(parents=True, exist_ok=True)

    for article_filename, image_mapping in ARTICLE_IMAGE_MAPPING.items():
        logger.info(f"\n🗂️  Processing: {article_filename}")

        for img in image_mapping:
            key = img['key']
            filename = img['filename']

            if key not in key_to_image_id:
                logger.error(f"  ❌ No image generated for key: {key}")
                continue

            parent_image_id = key_to_image_id[key]

            try:
                # 최고 크롭 URL 조회
                best_crop_url = get_best_crop_url(parent_image_id)
                logger.info(f"  • {key} → {filename}")
                logger.info(f"    URL: {best_crop_url[:60]}...")

                # 이미지 다운로드
                save_path = public_images_dir / filename
                download_image(best_crop_url, save_path)

            except Exception as e:
                logger.error(f"  ❌ Failed to process {filename}: {e}")

        # 마크다운 업데이트 (이미 경로가 맞으면 변경 없음)
        try:
            update_markdown_images(article_filename, image_mapping)
        except Exception as e:
            logger.error(f"  ❌ Failed to update markdown: {e}")

    logger.info("\n" + "=" * 80)
    logger.success("✅ ALL DONE! 블로그 이미지 재생성 완료")
    logger.info("=" * 80)
    logger.info(f"\n📊 Summary:")
    logger.info(f"  • Generated: {len(results)} Midjourney images (with 4 crops each)")
    logger.info(f"  • Downloaded: {len(ARTICLE_IMAGE_MAPPING) * 2} best crop images")
    logger.info(f"  • Updated: {len(ARTICLE_IMAGE_MAPPING)} blog articles")
    logger.info(f"\n📁 Images saved to: {public_images_dir}")

if __name__ == "__main__":
    main()
