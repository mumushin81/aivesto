#!/usr/bin/env python3
"""
모든 블로그 글의 이미지 연결 상태 확인
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

load_dotenv()

def check_all_blog_images():
    """모든 블로그 article_id에 대한 이미지 연결 확인"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL/KEY 설정 누락")
        return

    supabase = create_client(supabase_url, supabase_key)

    logger.info("=" * 60)
    logger.info("🔍 모든 블로그 글 이미지 연결 상태 확인")
    logger.info("=" * 60)

    # 모든 HTML 파일에서 article_id 추출
    articles_dir = Path("/Users/jinxin/dev/aivesto/public/articles")
    html_files = list(articles_dir.glob("article_*.html"))

    logger.info(f"\n📝 총 {len(html_files)}개 블로그 글 발견")

    # article_id 리스트 생성 (파일명에서 추출)
    article_ids = []
    for html_file in html_files:
        # article_NVDA_blackwell_gpu_20251113.html → nvda_blackwell_20251113
        filename = html_file.stem  # article_NVDA_blackwell_gpu_20251113
        parts = filename.replace('article_', '').split('_')

        if len(parts) >= 3:
            symbol = parts[0].lower()
            topic = '_'.join(parts[1:-1])
            date = parts[-1]
            article_id = f"{symbol}_{topic}_{date}"
            article_ids.append({
                'article_id': article_id,
                'filename': html_file.name,
                'symbol': symbol.upper()
            })

    logger.info(f"  ✅ {len(article_ids)}개 article_id 추출 완료\n")

    # 각 article_id에 대한 이미지 연결 확인
    articles_with_images = []
    articles_without_images = []

    for article in article_ids:
        article_id = article['article_id']

        try:
            result = supabase.table('blog_images') \
                .select('*, images(*)') \
                .eq('article_id', article_id) \
                .execute()

            if result.data and len(result.data) > 0:
                logger.success(f"✅ {article['filename']}")
                logger.info(f"   Article ID: {article_id}")
                logger.info(f"   이미지 수: {len(result.data)}개")

                # 크롭 여부 확인
                cropped_count = 0
                for record in result.data:
                    img = record.get('images', {})
                    img_url = img.get('image_url', '')
                    if '/cropped/' in img_url:
                        cropped_count += 1

                logger.info(f"   크롭 이미지: {cropped_count}/{len(result.data)}개\n")

                articles_with_images.append({
                    **article,
                    'image_count': len(result.data),
                    'cropped_count': cropped_count
                })
            else:
                logger.warning(f"⚠️  {article['filename']}")
                logger.warning(f"   Article ID: {article_id}")
                logger.warning(f"   이미지 없음\n")

                articles_without_images.append(article)

        except Exception as e:
            logger.error(f"❌ {article['filename']}: 조회 실패")
            logger.error(f"   {e}\n")
            articles_without_images.append(article)

    # 요약
    logger.info("=" * 60)
    logger.info("📊 요약")
    logger.info("=" * 60)
    logger.success(f"✅ 이미지 있음: {len(articles_with_images)}개")
    logger.warning(f"⚠️  이미지 없음: {len(articles_without_images)}개")

    if articles_without_images:
        logger.info("\n이미지가 없는 블로그 글:")
        for article in articles_without_images:
            logger.warning(f"  - {article['symbol']}: {article['article_id']}")

    return articles_with_images, articles_without_images


if __name__ == "__main__":
    with_images, without_images = check_all_blog_images()

    if without_images:
        logger.info("\n" + "=" * 60)
        logger.info(f"💡 {len(without_images)}개 블로그 글에 이미지를 생성해야 합니다")
        logger.info("=" * 60)
