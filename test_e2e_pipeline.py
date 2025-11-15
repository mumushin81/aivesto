#!/usr/bin/env python3
"""
엔드투엔드 파이프라인 통합 테스트
Layer 1/2 수집 → 분석 → 증폭 감지 → 저장
"""
import sys
sys.path.append('.')

from pipeline.news_pipeline import NewsPipeline
from database.supabase_client import SupabaseClient
from loguru import logger


def test_e2e_pipeline():
    """E2E 파이프라인 테스트"""
    logger.info("="*70)
    logger.info("🚀 End-to-End News Pipeline Test")
    logger.info("="*70)

    # Supabase 클라이언트 (옵션)
    db_client = None
    try:
        db_client = SupabaseClient()
        logger.info("✅ Supabase connected")
    except Exception as e:
        logger.warning(f"⚠️  Supabase not available: {e}")
        logger.info("ℹ️  Running in test mode without database")

    # 파이프라인 초기화
    pipeline = NewsPipeline(db_client=db_client, use_finbert=False)

    # 실행
    try:
        results = pipeline.run(save_to_db=(db_client is not None))

        # 결과 요약
        logger.info("\n" + "="*70)
        logger.info("📊 Pipeline Results Summary")
        logger.info("="*70)

        stats = results['stats']
        logger.info(f"\n📈 Collection:")
        logger.info(f"  Total Articles: {stats['total_articles']}")
        logger.info(f"  Layer 1 (Core Signal): {stats['layer1_count']}")
        logger.info(f"  Layer 2 (Sentiment & Momentum): {stats['layer2_count']}")

        logger.info(f"\n🔬 Analysis:")
        logger.info(f"  Analyzed Articles: {stats['analyzed_count']}")
        logger.info(f"  High Priority (80+): {stats['high_priority_count']}")
        logger.info(f"  Policy Signals Detected: {stats['policy_signals']}")

        logger.info(f"\n🔊 Amplification:")
        amp_results = results['amplification_results']
        logger.info(f"  Amplification Detected: {amp_results['has_amplification']}")
        logger.info(f"  Amplification Ratio: {amp_results['amplification_ratio']}")
        logger.info(f"  Amplification Level: {amp_results['amplification_level']}")

        if db_client:
            logger.info(f"\n💾 Database:")
            logger.info(f"  Saved to Supabase: {stats['saved_count']} articles")

        logger.info(f"\n⏱️  Performance:")
        logger.info(f"  Total Duration: {stats['duration_seconds']}s")

        # 샘플 결과 출력
        logger.info("\n" + "="*70)
        logger.info("📰 Sample High-Priority Articles")
        logger.info("="*70)

        high_priority = [
            a for a in results['analyzed_articles']
            if a['priority_score'] >= 80
        ][:5]  # 상위 5개

        for i, article in enumerate(high_priority, 1):
            raw = article['raw_news']
            logger.info(f"\n{i}. [{article['priority_score']}점] {raw.title[:80]}")
            logger.info(f"   Source: {raw.source}")
            logger.info(f"   Symbols: {article['symbols']}")
            logger.info(f"   Sentiment: {article['sentiment']} ({article['sentiment_score']:.2f})")
            if article['has_policy']:
                logger.info(f"   Policy: {article['policy_type']} - {article['policy_description'][:60]}")

        logger.info("\n" + "="*70)
        logger.info("✅ E2E Pipeline Test Completed Successfully!")
        logger.info("="*70)

    except Exception as e:
        logger.error(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    test_e2e_pipeline()
