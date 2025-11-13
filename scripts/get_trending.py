#!/usr/bin/env python3
"""
트렌딩 종목 확인 스크립트
최근 분석된 뉴스에서 가장 많이 언급된 종목 표시
"""

import sys
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.analysis_pipeline import AnalysisPipeline
from database.supabase_client import SupabaseClient

def show_trending_symbols(top_n: int = 10):
    """트렌딩 종목 표시"""

    db = SupabaseClient()
    pipeline = AnalysisPipeline(db)

    trending = pipeline.get_trending_symbols()

    if not trending:
        print("\n⚠️  No trending symbols found. Run analysis first.")
        return

    print(f"\n📈 Top {min(top_n, len(trending))} Trending Symbols\n")
    print("=" * 60)

    for i, (symbol, count) in enumerate(list(trending.items())[:top_n], 1):
        print(f"{i:2d}. {symbol:6s} - {count:3d} mentions")

    print("=" * 60)
    print(f"\nTotal symbols: {len(trending)}")

    # 상위 5개 추천
    top_5 = list(trending.keys())[:5]
    print(f"\n💡 Recommended for article generation: {', '.join(top_5)}")

    # 다음 명령 제안
    print("\n🔄 Next step:")
    print(f"python scripts/generate_article_prompts.py {' '.join(top_5[:3])}")

if __name__ == "__main__":
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    show_trending_symbols(top_n)
