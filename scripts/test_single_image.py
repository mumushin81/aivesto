#!/usr/bin/env python3
"""
테스트: Magic_book으로 단일 이미지 생성
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Magic_book 경로 추가
magic_book_path = Path("/Users/jinxin/dev/magic_book")
sys.path.insert(0, str(magic_book_path))

# aivesto .env 로드 (Supabase 설정용)
load_dotenv('/Users/jinxin/dev/aivesto/.env')

from loguru import logger

def test_single_image():
    """단일 이미지 생성 테스트"""

    # Magic_book의 Midjourney 모듈 임포트
    try:
        from src.midjourney import generate_images_batch_and_save
    except ImportError as e:
        logger.error(f"❌ magic_book 모듈 로드 실패: {e}")
        logger.info("magic_book 프로젝트 경로를 확인하세요: /Users/jinxin/dev/magic_book")
        return False

    # 테스트 프롬프트
    test_prompt = (
        "Modern technology visualization, abstract digital network with glowing green nodes, "
        "clean professional style, dark background, corporate presentation aesthetic, "
        "futuristic data flow --ar 16:9 --quality 1"
    )

    logger.info("=" * 60)
    logger.info("🧪 Midjourney 이미지 생성 테스트")
    logger.info("=" * 60)
    logger.info(f"📝 프롬프트: {test_prompt}")
    logger.info("")

    try:
        results = generate_images_batch_and_save(
            prompts=[test_prompt],
            request_delay=2.0,          # 2초 대기
            timeout_per_image=300,      # 5분 타임아웃
            auto_crop=False,            # 크롭 없이 원본만
            save_locally=False,         # 로컬 저장 안함 (Supabase만)
            verbose=True
        )

        if results and len(results) > 0:
            result = results[0]

            if result.success:
                logger.success("✅ 이미지 생성 성공!")
                # image_url이 아니라 image_urls (리스트)
                if hasattr(result, 'image_urls') and result.image_urls:
                    logger.info(f"   Image URL: {result.image_urls[0]}")
                if hasattr(result, 'supabase_image_ids') and result.supabase_image_ids:
                    logger.info(f"   Supabase ID: {result.supabase_image_ids[0]}")
                    logger.info(f"   Public URL: https://czubqsnahmtdsmnyawlk.supabase.co/storage/v1/object/public/midjourney-images/originals/{result.supabase_image_ids[0]}_*.png")
                return True
            else:
                logger.error(f"❌ 이미지 생성 실패: {result.error if hasattr(result, 'error') else 'Unknown error'}")
                return False
        else:
            logger.error("❌ 결과를 받지 못했습니다")
            return False

    except Exception as e:
        logger.error(f"❌ 이미지 생성 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_single_image()
    sys.exit(0 if success else 1)
