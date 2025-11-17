#!/usr/bin/env python3
"""
midjourney_images 테이블 스키마 확인
"""
import os
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

load_dotenv()

def inspect_schema():
    """midjourney_images 테이블 구조 확인"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL/KEY 설정 누락")
        return

    supabase = create_client(supabase_url, supabase_key)

    logger.info("=" * 60)
    logger.info("🔍 midjourney_images 테이블 스키마 조사")
    logger.info("=" * 60)

    try:
        # 샘플 데이터 가져오기
        result = supabase.table('midjourney_images') \
            .select('*') \
            .limit(3) \
            .execute()

        if result.data:
            logger.success(f"\n✅ {len(result.data)}개 샘플 레코드 발견")

            for idx, record in enumerate(result.data, 1):
                logger.info(f"\n레코드 {idx}:")
                logger.info(f"  컬럼: {list(record.keys())}")

                for key, value in record.items():
                    if isinstance(value, str) and len(value) > 80:
                        logger.info(f"    {key}: {value[:80]}...")
                    else:
                        logger.info(f"    {key}: {value}")

        else:
            logger.warning("❌ midjourney_images 테이블이 비어있음")

    except Exception as e:
        logger.error(f"❌ 조회 실패: {e}")
        import traceback
        traceback.print_exc()

    # cropped 이미지 찾기
    logger.info("\n" + "=" * 60)
    logger.info("🔍 cropped 이미지 검색")
    logger.info("=" * 60)

    try:
        cropped_result = supabase.table('midjourney_images') \
            .select('*') \
            .eq('image_type', 'cropped') \
            .limit(5) \
            .execute()

        if cropped_result.data:
            logger.success(f"\n✅ {len(cropped_result.data)}개 cropped 이미지 발견")

            for idx, record in enumerate(cropped_result.data, 1):
                logger.info(f"\nCropped 이미지 {idx}:")
                logger.info(f"  ID: {record.get('id')}")
                logger.info(f"  URL: {record.get('public_url', '')[:80]}...")
                logger.info(f"  Prompt: {record.get('prompt', '')[:60]}...")
                logger.info(f"  전체 컬럼: {list(record.keys())}")

        else:
            logger.warning("❌ cropped 이미지가 하나도 없음")

    except Exception as e:
        logger.error(f"❌ cropped 이미지 조회 실패: {e}")


if __name__ == "__main__":
    inspect_schema()
