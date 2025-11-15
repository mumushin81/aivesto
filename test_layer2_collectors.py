#!/usr/bin/env python3
"""
Layer 2 수집기 테스트 스크립트
Fox News, CNN, Yahoo Finance RSS 피드 테스트
"""
import sys
sys.path.append('.')

from collectors.fox_collector import FoxCollector
from collectors.cnn_collector import CNNCollector
from collectors.yahoo_collector import YahooCollector
from database.supabase_client import SupabaseClient
from loguru import logger

def test_collectors():
    """Layer 2 수집기 테스트"""

    logger.info("="*60)
    logger.info("Layer 2 Collectors Test (Sentiment & Momentum)")
    logger.info("="*60)

    try:
        # Supabase 클라이언트 (실패해도 괜찮음)
        try:
            db = SupabaseClient()
            logger.info("✅ Supabase connected")
        except:
            db = None
            logger.warning("⚠️  Supabase not available, testing RSS only")

        # Fox News 테스트
        logger.info("\n📺 Testing Fox News Collector...")
        fox = FoxCollector(db)
        fox_news = fox.fetch_news()
        logger.info(f"   Collected: {len(fox_news)} articles")

        if fox_news:
            sample = fox_news[0]
            logger.info(f"   Sample: {sample.title[:80]}")
            logger.info(f"   URL: {sample.url}")

        # CNN 테스트
        logger.info("\n📺 Testing CNN Collector...")
        cnn = CNNCollector(db)
        cnn_news = cnn.fetch_news()
        logger.info(f"   Collected: {len(cnn_news)} articles")

        if cnn_news:
            sample = cnn_news[0]
            logger.info(f"   Sample: {sample.title[:80]}")
            logger.info(f"   URL: {sample.url}")

        # Yahoo Finance 테스트
        logger.info("\n💹 Testing Yahoo Finance Collector...")
        yahoo = YahooCollector(db)
        yahoo_news = yahoo.fetch_news()
        logger.info(f"   Collected: {len(yahoo_news)} articles")

        if yahoo_news:
            sample = yahoo_news[0]
            logger.info(f"   Sample: {sample.title[:80]}")
            logger.info(f"   URL: {sample.url}")

        # 요약
        total = len(fox_news) + len(cnn_news) + len(yahoo_news)
        logger.info("\n"+"="*60)
        logger.info(f"✅ Total Layer 2 articles collected: {total}")
        logger.info(f"   Fox News: {len(fox_news)}")
        logger.info(f"   CNN: {len(cnn_news)}")
        logger.info(f"   Yahoo Finance: {len(yahoo_news)}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_collectors()
