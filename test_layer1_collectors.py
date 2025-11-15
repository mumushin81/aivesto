#!/usr/bin/env python3
"""
Layer 1 수집기 테스트 스크립트
Bloomberg, Reuters, WSJ RSS 피드 테스트
"""
from collectors.bloomberg_collector import BloombergCollector
from collectors.reuters_collector import ReutersCollector
from collectors.wsj_collector import WSJCollector
from database.supabase_client import SupabaseClient
from loguru import logger

def test_collectors():
    """Layer 1 수집기 테스트"""

    logger.info("="*60)
    logger.info("Layer 1 Collectors Test")
    logger.info("="*60)

    try:
        # Supabase 클라이언트 (실패해도 괜찮음)
        try:
            db = SupabaseClient()
            logger.info("✅ Supabase connected")
        except:
            db = None
            logger.warning("⚠️  Supabase not available, testing RSS only")

        # Bloomberg 테스트
        logger.info("\n📰 Testing Bloomberg Collector...")
        bloomberg = BloombergCollector(db)
        bloomberg_news = bloomberg.fetch_news()
        logger.info(f"   Collected: {len(bloomberg_news)} articles")

        if bloomberg_news:
            sample = bloomberg_news[0]
            logger.info(f"   Sample: {sample.title[:80]}")
            logger.info(f"   URL: {sample.url}")

        # Reuters 테스트
        logger.info("\n📰 Testing Reuters Collector...")
        reuters = ReutersCollector(db)
        reuters_news = reuters.fetch_news()
        logger.info(f"   Collected: {len(reuters_news)} articles")

        if reuters_news:
            sample = reuters_news[0]
            logger.info(f"   Sample: {sample.title[:80]}")
            logger.info(f"   URL: {sample.url}")

        # WSJ 테스트
        logger.info("\n📰 Testing WSJ Collector...")
        wsj = WSJCollector(db)
        wsj_news = wsj.fetch_news()
        logger.info(f"   Collected: {len(wsj_news)} articles")

        if wsj_news:
            sample = wsj_news[0]
            logger.info(f"   Sample: {sample.title[:80]}")
            logger.info(f"   URL: {sample.url}")

        # 요약
        total = len(bloomberg_news) + len(reuters_news) + len(wsj_news)
        logger.info("\n"+"="*60)
        logger.info(f"✅ Total Layer 1 articles collected: {total}")
        logger.info(f"   Bloomberg: {len(bloomberg_news)}")
        logger.info(f"   Reuters: {len(reuters_news)}")
        logger.info(f"   WSJ: {len(wsj_news)}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_collectors()
