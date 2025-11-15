#!/usr/bin/env python3
"""
Test MCP Integration - Claude Code와 Supabase MCP 서버 연동 테스트
"""

import sys
sys.path.append('.')

from database.supabase_client import SupabaseClient
from database.models import RawNews, AnalyzedNews, PriceImpact, Importance
from datetime import datetime
from loguru import logger

def insert_sample_data():
    """테스트용 샘플 데이터 삽입"""
    client = SupabaseClient()

    logger.info("샘플 데이터 삽입 시작...")

    # 1. 원본 뉴스 3개 삽입
    sample_news = [
        RawNews(
            source="Reuters",
            title="NVIDIA announces new AI chip breakthrough",
            url="https://example.com/nvidia-ai-chip-1",
            content="NVIDIA Corporation announced a major breakthrough in AI chip technology...",
            published_at=datetime.now(),
            symbols=["NVDA"],
            metadata={"category": "technology", "priority": "high"}
        ),
        RawNews(
            source="Bloomberg",
            title="Microsoft expands cloud services to new markets",
            url="https://example.com/msft-cloud-expansion-2",
            content="Microsoft Corporation is expanding its Azure cloud services...",
            published_at=datetime.now(),
            symbols=["MSFT"],
            metadata={"category": "technology", "priority": "medium"}
        ),
        RawNews(
            source="MarketWatch",
            title="Tesla reports record quarterly deliveries",
            url="https://example.com/tesla-deliveries-3",
            content="Tesla Inc. has reported record-breaking quarterly vehicle deliveries...",
            published_at=datetime.now(),
            symbols=["TSLA"],
            metadata={"category": "automotive", "priority": "high"}
        )
    ]

    raw_news_ids = []
    for news in sample_news:
        news_id = client.insert_raw_news(news)
        if news_id:
            raw_news_ids.append(news_id)
            logger.success(f"✓ Inserted raw news: {news.title[:50]}...")

    # 2. 분석된 뉴스 3개 삽입
    analyzed_samples = [
        AnalyzedNews(
            raw_news_id=raw_news_ids[0],
            relevance_score=95,
            affected_symbols=["NVDA", "AMD", "INTC"],
            price_impact=PriceImpact.UP,
            importance=Importance.HIGH,
            analysis={
                "summary": "Major AI chip breakthrough could boost semiconductor stocks",
                "key_points": ["New architecture", "Performance gains", "Market impact"],
                "sentiment": "very positive"
            },
            signal_level=1  # Urgent
        ),
        AnalyzedNews(
            raw_news_id=raw_news_ids[1],
            relevance_score=78,
            affected_symbols=["MSFT", "GOOGL", "AMZN"],
            price_impact=PriceImpact.UP,
            importance=Importance.MEDIUM,
            analysis={
                "summary": "Cloud expansion indicates strong growth trajectory",
                "key_points": ["Market expansion", "Revenue growth", "Competition"],
                "sentiment": "positive"
            },
            signal_level=2  # High
        ),
        AnalyzedNews(
            raw_news_id=raw_news_ids[2],
            relevance_score=88,
            affected_symbols=["TSLA"],
            price_impact=PriceImpact.UP,
            importance=Importance.HIGH,
            analysis={
                "summary": "Record deliveries exceed analyst expectations",
                "key_points": ["Production scale", "Market demand", "Revenue impact"],
                "sentiment": "positive"
            },
            signal_level=1  # Urgent
        )
    ]

    for analyzed in analyzed_samples:
        analyzed_id = client.insert_analyzed_news(analyzed)
        if analyzed_id:
            logger.success(f"✓ Inserted analyzed news (score: {analyzed.relevance_score})")

    logger.success("\n✅ 샘플 데이터 삽입 완료!")
    return True

def test_mcp_methods():
    """MCP 서버 메서드 테스트"""
    client = SupabaseClient()

    logger.info("\n" + "="*60)
    logger.info("MCP 메서드 테스트 시작")
    logger.info("="*60)

    # 1. Dashboard Stats
    logger.info("\n[1] get_dashboard_stats 테스트")
    stats = client.get_dashboard_stats()
    logger.info(f"  - Total articles: {stats['total_articles']}")
    logger.info(f"  - High priority: {stats['high_priority_count']}")
    logger.info(f"  - Last 1h: {stats['last_1h_count']}")

    # 2. High Relevance News
    logger.info("\n[2] get_high_relevance_news 테스트")
    high_news = client.get_high_relevance_news(min_score=70, limit=10)
    logger.info(f"  - Found {len(high_news)} high-relevance news items")
    for news in high_news[:3]:
        logger.info(f"    • Score: {news['relevance_score']}, Symbols: {news['affected_symbols']}")

    # 3. Trending Symbols
    logger.info("\n[3] get_trending_symbols 테스트")
    trending = client.get_trending_symbols(hours=24, limit=10)
    logger.info(f"  - Found {len(trending)} trending symbols")
    for symbol_data in trending[:5]:
        logger.info(f"    • {symbol_data['symbol']}: {symbol_data['count']} mentions, "
                   f"avg score: {symbol_data['avg_score']:.1f}")

    # 4. Signals by Level
    logger.info("\n[4] get_signals_by_level 테스트 (Level 1 - Urgent)")
    urgent_signals = client.get_signals_by_level(level=1, hours=24, limit=20)
    logger.info(f"  - Found {len(urgent_signals)} urgent signals")
    for signal in urgent_signals[:3]:
        logger.info(f"    • Score: {signal['relevance_score']}, Symbols: {signal['affected_symbols']}")

    # 5. Important Symbols Today
    logger.info("\n[5] get_important_symbols_today 테스트")
    important = client.get_important_symbols_today()
    logger.info(f"  - Found {len(important)} important symbols")
    for symbol_data in important[:3]:
        logger.info(f"    • {symbol_data['symbol']}: {symbol_data['urgent_count']} urgent, "
                   f"{symbol_data['signals']} total signals")

    # 6. Articles for Dashboard
    logger.info("\n[6] get_articles_for_dashboard 테스트")
    articles = client.get_articles_for_dashboard(limit=5, min_priority=0)
    logger.info(f"  - Found {len(articles)} articles")
    for article in articles[:3]:
        logger.info(f"    • {article['title'][:60]}...")
        logger.info(f"      Priority: {article['priority_score']}, Symbols: {article['symbols']}")

    logger.info("\n" + "="*60)
    logger.success("✅ MCP 메서드 테스트 완료!")
    logger.info("="*60)

def main():
    """메인 함수"""
    print("\n" + "="*70)
    print("  Claude Code + Supabase MCP Integration Test")
    print("="*70)

    choice = input("\n샘플 데이터를 삽입하시겠습니까? (y/n): ").lower()

    if choice == 'y':
        insert_sample_data()

    input("\nEnter를 눌러 MCP 메서드 테스트를 시작하세요...")
    test_mcp_methods()

    print("\n" + "="*70)
    print("  이제 Claude Code에서 다음과 같이 MCP를 사용할 수 있습니다:")
    print("="*70)
    print("""
    예시 1: "Supabase에서 대시보드 통계를 가져와줘"
    예시 2: "오늘 긴급 신호가 있는 종목을 보여줘"
    예시 3: "최근 24시간 동안 가장 많이 언급된 종목 상위 5개는?"
    예시 4: "NVDA 관련 뉴스를 우선순위 순으로 보여줘"
    """)
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
