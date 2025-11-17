#!/usr/bin/env python3
"""
기존에 생성된 Midjourney 이미지들을 블로그 글에 연결
"""
import os
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

load_dotenv()

def connect_existing_images():
    """기존 Midjourney 이미지를 blog_images에 연결"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL/KEY 설정 누락")
        return False

    supabase = create_client(supabase_url, supabase_key)

    logger.info("=" * 60)
    logger.info("🔗 기존 Midjourney 이미지를 블로그 글에 연결")
    logger.info("=" * 60)

    # 1단계: midjourney_images에서 원본(original) 이미지 가져오기
    logger.info("\n📝 1단계: Midjourney 원본 이미지 조회 중...")

    try:
        # 테스트 이미지 제외하고 원본만
        mj_result = supabase.table('midjourney_images') \
            .select('*') \
            .eq('image_type', 'original') \
            .order('created_at', desc=False) \
            .execute()

        original_images = mj_result.data
        logger.info(f"  ✅ {len(original_images)}개 원본 이미지 발견")

        # 최근 5개만 사용 (테스트 이미지들)
        if len(original_images) > 5:
            logger.info(f"  ℹ️  최근 5개 이미지만 사용")
            original_images = original_images[-5:]  # 최신 5개

        for idx, img in enumerate(original_images, 1):
            logger.info(f"  {idx}. {img.get('prompt', '')[:60]}...")
            logger.info(f"     URL: {img.get('public_url', '')[:60]}...")

    except Exception as e:
        logger.error(f"❌ Midjourney 이미지 조회 실패: {e}")
        return False

    # 2단계: images 테이블에 저장 및 blog_images 연결
    logger.info("\n📝 2단계: images 테이블에 저장 및 blog_images 연결 중...")

    article_id = "nvda_blackwell_20251113"

    connected_count = 0

    for idx, mj_img in enumerate(original_images):
        try:
            # images 테이블에 저장
            image_data = {
                "symbol": "NVDA",
                "topic": "blackwell_gpu",
                "prompt": mj_img.get('prompt', ''),
                "image_url": mj_img.get('public_url', '')
            }

            # 이미 존재하는지 확인
            existing = supabase.table('images') \
                .select('id') \
                .eq('image_url', image_data['image_url']) \
                .execute()

            if existing.data:
                image_id = existing.data[0]['id']
                logger.info(f"  {idx+1}. 이미 존재하는 이미지: {image_id}")
            else:
                result = supabase.table('images').insert(image_data).execute()

                if result.data:
                    image_id = result.data[0]['id']
                    logger.success(f"  {idx+1}. ✅ images 테이블 저장: {image_id}")
                else:
                    logger.error(f"  {idx+1}. ❌ images 저장 실패")
                    continue

            # blog_images에 연결 (중복 확인)
            blog_check = supabase.table('blog_images') \
                .select('*') \
                .eq('article_id', article_id) \
                .eq('image_id', image_id) \
                .execute()

            if blog_check.data:
                logger.info(f"       이미 연결됨 (position: {blog_check.data[0].get('position')})")
            else:
                blog_image_data = {
                    "article_id": article_id,
                    "image_id": image_id,
                    "position": idx
                }

                blog_result = supabase.table('blog_images').insert(blog_image_data).execute()

                if blog_result.data:
                    logger.success(f"       ✅ blog_images 연결 완료 (position: {idx})")
                    connected_count += 1
                else:
                    logger.error(f"       ❌ blog_images 연결 실패")

        except Exception as e:
            logger.error(f"  {idx+1}. ❌ 저장 실패: {e}")
            continue

    # 3단계: 검증
    logger.info("\n📝 3단계: 연결 결과 검증 중...")

    try:
        verify_result = supabase.table('blog_images') \
            .select('*, images(*)') \
            .eq('article_id', article_id) \
            .order('position') \
            .execute()

        if verify_result.data:
            logger.success(f"\n✅ 검증 완료! {len(verify_result.data)}개 이미지 연결됨")
            logger.info(f"\n블로그 글: {article_id}")
            logger.info("연결된 이미지:")

            for record in verify_result.data:
                img = record.get('images', {})
                logger.info(f"  Position {record.get('position')}: {img.get('image_url', '')[:70]}...")

            return True
        else:
            logger.warning("❌ blog_images 테이블이 비어있음")
            return False

    except Exception as e:
        logger.error(f"❌ 검증 실패: {e}")
        return False


if __name__ == "__main__":
    success = connect_existing_images()

    if success:
        logger.success("\n" + "=" * 60)
        logger.success("🎉 기존 이미지 연결 완료!")
        logger.success("=" * 60)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("❌ 이미지 연결 실패")
        logger.error("=" * 60)
