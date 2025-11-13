#!/usr/bin/env python3
"""
작성한 블로그 글을 Supabase에 저장하는 스크립트
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.supabase_client import SupabaseClient
from database.models import PublishedArticle

def extract_metadata_from_filename(filename: str):
    """파일명에서 종목 심볼과 타임스탬프 추출"""
    # article_AAPL_20251112_1000.md
    match = re.search(r'article_([A-Z]+)_(\d{8}_\d{4})\.md', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def publish_article(article_file: str):
    """블로그 글을 데이터베이스에 저장"""

    try:
        # 파일 읽기
        with open(article_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 제목 추출 (첫 번째 # 헤더)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            logger.error(f"No title found in {article_file}")
            return False

        title = title_match.group(1).strip()

        # 파일명에서 메타데이터 추출
        filename = Path(article_file).name
        symbol, timestamp = extract_metadata_from_filename(filename)

        # Supabase 연결
        db = SupabaseClient()

        # 관련 뉴스 ID 찾기 (해당 종목 관련)
        analyzed_news_ids = []
        if symbol:
            news_items = db.get_unpublished_news_by_symbol(symbol, limit=5)
            analyzed_news_ids = [news['id'] for news in news_items]

        # 발행 글 저장
        article = PublishedArticle(
            title=title,
            content=content,
            analyzed_news_ids=analyzed_news_ids,
            published_at=datetime.now()
        )

        article_id = db.insert_published_article(article)

        if article_id:
            logger.info(f"Published article: {title[:50]}... (ID: {article_id})")
            return True
        else:
            logger.error(f"Failed to publish article: {title[:50]}...")
            return False

    except FileNotFoundError:
        logger.error(f"File not found: {article_file}")
        return False
    except Exception as e:
        logger.error(f"Error publishing article: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/publish_articles.py <article_file1> [article_file2] ...")
        print("Example: python scripts/publish_articles.py articles/article_AAPL_20251112_1000.md")
        sys.exit(1)

    article_files = sys.argv[1:]
    success_count = 0

    print(f"\n📤 Publishing {len(article_files)} articles...\n")

    for article_file in article_files:
        if publish_article(article_file):
            success_count += 1
            print(f"✅ {article_file}")
        else:
            print(f"❌ {article_file}")

    print(f"\n{'='*60}")
    print(f"Published: {success_count}/{len(article_files)} articles")
    print(f"{'='*60}\n")

    if success_count > 0:
        print("🎉 Articles successfully published to database!")
        print("\nView in Supabase:")
        print("SELECT title, created_at FROM published_articles ORDER BY created_at DESC LIMIT 10;")
    else:
        print("⚠️  No articles were published")
        sys.exit(1)
