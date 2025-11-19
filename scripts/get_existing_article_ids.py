#!/usr/bin/env python3
"""
blog_images 테이블에 이미 존재하는 article_id 확인
"""
import os
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

load_dotenv()

def get_existing_article_ids():
    """blog_images에서 이미 이미지가 있는 article_id 조회"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL/KEY 설정 누락")
        return

    supabase = create_client(supabase_url, supabase_key)

    logger.info("=" * 60)
    logger.info("🔍 blog_images 테이블의 기존 article_id 조회")
    logger.info("=" * 60)

    try:
        # blog_images 테이블의 모든 레코드 조회
        result = supabase.table('blog_images') \
            .select('article_id, image_id, position') \
            .order('article_id') \
            .execute()

        if result.data:
            logger.success(f"\n✅ {len(result.data)}개 레코드 발견")

            # article_id별 그룹화
            article_groups = {}
            for record in result.data:
                article_id = record.get('article_id')
                if article_id not in article_groups:
                    article_groups[article_id] = []
                article_groups[article_id].append(record)

            logger.info(f"\n📊 총 {len(article_groups)}개 article_id:")
            for article_id, records in article_groups.items():
                logger.info(f"\n  {article_id}:")
                logger.info(f"    이미지 수: {len(records)}개")
                for record in records:
                    logger.info(f"      Position {record.get('position')}: Image ID {record.get('image_id')}")

        else:
            logger.warning("❌ blog_images 테이블이 비어있음")

    except Exception as e:
        logger.error(f"❌ 조회 실패: {e}")


if __name__ == "__main__":
    get_existing_article_ids()
