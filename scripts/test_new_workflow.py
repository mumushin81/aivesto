#!/usr/bin/env python3
"""
새로운 워크플로우 테스트: 1개 이미지만 생성
다운로드 → 크롭 → 선정 → Supabase 저장
"""
import os
import sys
import requests
from pathlib import Path
from typing import List, Tuple

# magic_book 모듈 import
magic_book_path = Path.home() / 'dev' / 'magic_book'
sys.path.insert(0, str(magic_book_path))

from dotenv import load_dotenv
from loguru import logger
from src.midjourney.client import PassPromptToSelfBot, wait_for_image_completion
from src.midjourney.processor import crop_image_cross
from src.midjourney.storage import MidjourneyImageStorage

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 테스트 프롬프트
TEST_PROMPT = "Futuristic NVIDIA GPU chip with glowing green circuits, ultra-detailed 3D render, dramatic studio lighting, floating semiconductor design, black background with subtle green accents, professional tech photography, 8k quality --ar 16:9 --quality 2 --stylize 500"

def generate_midjourney_image(prompt: str, timeout: int = 300) -> str:
    """
    Midjourney 이미지 생성 및 URL 반환 (Supabase 저장 없음)
    """
    import time

    logger.info(f"📤 프롬프트 전송...")
    logger.info(f"   {prompt[:80]}...")

    request_timestamp = time.time()
    response = PassPromptToSelfBot(prompt)

    if response.status_code != 204:
        logger.error(f"❌ 이미지 생성 요청 실패: HTTP {response.status_code}")
        return None

    logger.info("⏳ 이미지 완성 대기 중 (최대 5분)...")
    image_urls = wait_for_image_completion(
        prompt=prompt,
        request_timestamp=request_timestamp,
        timeout=timeout,
        check_interval=5
    )

    if not image_urls:
        logger.error("❌ 이미지 생성 타임아웃")
        return None

    logger.success(f"✅ 이미지 생성 완료!")
    return image_urls[0]

def download_and_crop_locally(image_url: str, save_dir: Path) -> Tuple[Path, List[Path]]:
    """
    이미지 다운로드 및 로컬 크롭
    """
    # 원본 다운로드
    save_dir.mkdir(parents=True, exist_ok=True)
    original_path = save_dir / "original.jpg"

    logger.info(f"📥 원본 이미지 다운로드 중...")
    logger.info(f"   URL: {image_url[:60]}...")

    response = requests.get(image_url)
    response.raise_for_status()

    with open(original_path, 'wb') as f:
        f.write(response.content)

    file_size = os.path.getsize(original_path) / 1024 / 1024  # MB
    logger.success(f"✅ 원본 저장 완료: {original_path.name} ({file_size:.1f} MB)")

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

def select_best_crop(crop_paths: List[Path]) -> Path:
    """
    최고 크롭 선정 (현재는 top_left 선택)
    TODO: Claude Vision API 연동
    """
    best_crop = crop_paths[0]  # top_left
    logger.info(f"🤖 AI 선정 크롭: {best_crop.name} (top_left)")
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
    logger.info("🧪 새로운 워크플로우 테스트 (1개 이미지)")
    logger.info("=" * 80)
    logger.info("")
    logger.info("워크플로우:")
    logger.info("  1️⃣  Midjourney 이미지 생성")
    logger.info("  2️⃣  로컬 다운로드")
    logger.info("  3️⃣  로컬에서 4개 크롭 생성")
    logger.info("  4️⃣  AI가 최고 크롭 선정")
    logger.info("  5️⃣  선정된 크롭만 Supabase 저장 (원본은 로컬에만)")
    logger.info("")
    logger.info("=" * 80)

    # 작업 디렉토리 생성
    work_dir = Path(__file__).parent.parent / 'temp_images' / 'test'
    work_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 작업 디렉토리: {work_dir}")
    logger.info("")

    try:
        # 1. Midjourney 이미지 생성
        logger.info("🎨 Step 1/5: Midjourney 이미지 생성")
        image_url = generate_midjourney_image(TEST_PROMPT, timeout=300)
        if not image_url:
            logger.error("❌ 이미지 생성 실패")
            return
        logger.info("")

        # 2. 로컬 다운로드 + 크롭
        logger.info("📦 Step 2-3/5: 로컬 다운로드 및 크롭")
        original_path, crop_paths = download_and_crop_locally(image_url, work_dir)
        logger.info("")

        # 3. AI 최고 크롭 선정
        logger.info("🎯 Step 4/5: 최고 크롭 선정")
        best_crop = select_best_crop(crop_paths)
        logger.info("")

        # 4. Supabase 업로드 (선정된 크롭만)
        logger.info("☁️  Step 5/5: Supabase 업로드 (선정된 크롭만)")
        result = upload_to_supabase(best_crop, TEST_PROMPT)
        logger.info("")

        if result:
            logger.info("=" * 80)
            logger.success("✅ 테스트 성공!")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📊 결과:")
            logger.info(f"   • 크롭 ID: {result['crop_id']}")
            logger.info(f"   • 크롭 URL: {result['crop_url']}")
            logger.info(f"   • 원본 파일: {original_path} (로컬에만 저장)")
            logger.info("")
            logger.info(f"📁 로컬 파일: {work_dir}")
        else:
            logger.error("❌ 업로드 실패")

    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
