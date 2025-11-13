#!/usr/bin/env python3
"""
블로그 글 작성 프롬프트 생성 스크립트
지정된 종목에 대한 글 작성 프롬프트를 생성
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.supabase_client import SupabaseClient
from analyzers.prompt_generator import PromptGenerator

def generate_prompts(symbols: list, output_dir: str = "prompts"):
    """종목별 글 작성 프롬프트 생성"""

    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    db = SupabaseClient()
    generator = PromptGenerator(db)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    generated_files = []

    for symbol in symbols:
        # 해당 종목 관련 뉴스 가져오기
        news_items = db.get_unpublished_news_by_symbol(symbol, limit=5)

        if not news_items:
            logger.warning(f"No unpublished news found for {symbol}")
            continue

        # 프롬프트 생성
        output_file = f"{output_dir}/article_{symbol}_{timestamp}.md"
        generator.generate_article_prompt(symbol, news_items, output_file)

        generated_files.append((symbol, output_file, len(news_items)))

    # 결과 출력
    print(f"\n✅ Generated {len(generated_files)} article prompts\n")
    print("=" * 70)

    for symbol, file, news_count in generated_files:
        print(f"📝 {symbol:6s} - {news_count} news items → {file}")

    print("=" * 70)

    if generated_files:
        print("\n🔄 Next steps:")
        print("1. Open each prompt file")
        print("2. Use Claude Code to write articles based on the prompts")
        print("3. Save articles as .md files in 'articles/' directory")
        print("4. Run: python scripts/publish_articles.py articles/article_*.md")

    return generated_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_article_prompts.py <SYMBOL1> <SYMBOL2> ...")
        print("Example: python scripts/generate_article_prompts.py AAPL TSLA NVDA")
        sys.exit(1)

    symbols = sys.argv[1:]
    generate_prompts(symbols)
