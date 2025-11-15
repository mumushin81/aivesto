#!/usr/bin/env python3
"""
Phase 3 증폭 감지 테스트
Layer 1 vs Layer 2 여론 증폭 효과 탐지
"""
from datetime import datetime, timedelta
from analyzers.amplification_detector import AmplificationDetector
from loguru import logger


def test_amplification():
    """증폭 감지 테스트"""
    logger.info("\n" + "="*60)
    logger.info("🔊 Testing Amplification Detector")
    logger.info("="*60)

    detector = AmplificationDetector(time_window_hours=24)

    # 가상의 Layer 1 뉴스 (Core Signal - 적은 수)
    layer1_articles = [
        {
            'title': 'Federal Reserve Raises Interest Rates by 0.25%',
            'source': 'Bloomberg (Layer 1)',
            'symbols': ['SPY', 'QQQ'],
            'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'metadata': {'sentiment_score': -0.2}
        },
        {
            'title': 'SEC Announces New Cryptocurrency Trading Rules',
            'source': 'Reuters (Layer 1)',
            'symbols': ['COIN', 'MSTR'],
            'published_at': (datetime.now() - timedelta(hours=3)).isoformat(),
            'metadata': {'sentiment_score': -0.3}
        },
        {
            'title': 'Tesla Reports Q4 Earnings Beat Expectations',
            'source': 'WSJ (Layer 1)',
            'symbols': ['TSLA'],
            'published_at': (datetime.now() - timedelta(hours=1)).isoformat(),
            'metadata': {'sentiment_score': 0.5}
        }
    ]

    # 가상의 Layer 2 뉴스 (Sentiment & Momentum - 많은 수)
    layer2_articles = [
        # Fed 관련 증폭 (6개)
        {
            'title': 'Federal Reserve Rate Hike Shocks Markets',
            'source': 'Fox News (Layer 2)',
            'symbols': ['SPY'],
            'published_at': (datetime.now() - timedelta(hours=1)).isoformat(),
            'metadata': {'sentiment_score': -0.5}
        },
        {
            'title': 'CNN: Federal Reserve Decision Sparks Recession Fears',
            'source': 'CNN (Layer 2)',
            'symbols': ['QQQ'],
            'published_at': (datetime.now() - timedelta(hours=1)).isoformat(),
            'metadata': {'sentiment_score': -0.6}
        },
        {
            'title': 'Yahoo: What Federal Reserve Rate Increase Means for Your Portfolio',
            'source': 'Yahoo Finance (Layer 2)',
            'symbols': ['SPY', 'QQQ'],
            'published_at': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'metadata': {'sentiment_score': -0.4}
        },
        {
            'title': 'Interest Rates Soar: Federal Reserve Takes Aggressive Stance',
            'source': 'Fox News (Layer 2)',
            'symbols': ['SPY'],
            'published_at': (datetime.now() - timedelta(minutes=45)).isoformat(),
            'metadata': {'sentiment_score': -0.5}
        },
        {
            'title': 'Federal Reserve Policy Shift: Winners and Losers',
            'source': 'CNN (Layer 2)',
            'symbols': ['QQQ'],
            'published_at': (datetime.now() - timedelta(minutes=20)).isoformat(),
            'metadata': {'sentiment_score': -0.3}
        },
        {
            'title': 'Breaking: Federal Reserve Moves to Combat Inflation',
            'source': 'Yahoo Finance (Layer 2)',
            'symbols': ['SPY'],
            'published_at': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'metadata': {'sentiment_score': -0.4}
        },

        # SEC 암호화폐 규제 증폭 (4개)
        {
            'title': 'SEC Cryptocurrency Crackdown Sends Bitcoin Tumbling',
            'source': 'Fox News (Layer 2)',
            'symbols': ['COIN'],
            'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'metadata': {'sentiment_score': -0.7}
        },
        {
            'title': 'CNN: New SEC Rules Could Kill Crypto Industry',
            'source': 'CNN (Layer 2)',
            'symbols': ['COIN', 'MSTR'],
            'published_at': (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
            'metadata': {'sentiment_score': -0.8}
        },
        {
            'title': 'Cryptocurrency Exchanges React to SEC Announcement',
            'source': 'Yahoo Finance (Layer 2)',
            'symbols': ['COIN'],
            'published_at': (datetime.now() - timedelta(minutes=40)).isoformat(),
            'metadata': {'sentiment_score': -0.6}
        },
        {
            'title': 'SEC Takes Aim at Cryptocurrency Trading Platforms',
            'source': 'CNN (Layer 2)',
            'symbols': ['COIN'],
            'published_at': (datetime.now() - timedelta(minutes=25)).isoformat(),
            'metadata': {'sentiment_score': -0.7}
        },

        # Tesla 관련 (2개 - 낮은 증폭)
        {
            'title': 'Tesla Earnings: What You Need to Know',
            'source': 'Yahoo Finance (Layer 2)',
            'symbols': ['TSLA'],
            'published_at': (datetime.now() - timedelta(minutes=50)).isoformat(),
            'metadata': {'sentiment_score': 0.3}
        },
        {
            'title': 'Tesla Stock Jumps on Strong Q4 Results',
            'source': 'Fox News (Layer 2)',
            'symbols': ['TSLA'],
            'published_at': (datetime.now() - timedelta(minutes=35)).isoformat(),
            'metadata': {'sentiment_score': 0.4}
        }
    ]

    # 전체 증폭 감지
    logger.info("\n📊 Overall Amplification Detection:")
    result = detector.detect_amplification(layer1_articles, layer2_articles)
    logger.info(f"   Has Amplification: {result['has_amplification']}")
    logger.info(f"   Amplification Ratio: {result['amplification_ratio']} (L2/L1)")
    logger.info(f"   Layer 1 Articles: {result['layer1_count']}")
    logger.info(f"   Layer 2 Articles: {result['layer2_count']}")
    logger.info(f"   Matched Topics: {result['matched_topics']}")
    logger.info(f"   Sentiment Shift: {result['sentiment_shift']}")
    logger.info(f"   Amplification Level: {result['amplification_level']}")

    # 심볼별 증폭 감지 (Fed 관련 - SPY)
    logger.info("\n📊 Symbol-Specific Amplification (SPY - Fed Rate Hike):")
    spy_result = detector.detect_amplification(layer1_articles, layer2_articles, symbols=['SPY'])
    logger.info(f"   Has Amplification: {spy_result['has_amplification']}")
    logger.info(f"   Amplification Ratio: {spy_result['amplification_ratio']}")
    logger.info(f"   Layer 1: {spy_result['layer1_count']}, Layer 2: {spy_result['layer2_count']}")
    logger.info(f"   Amplification Level: {spy_result['amplification_level']}")

    # 심볼별 증폭 감지 (암호화폐 - COIN)
    logger.info("\n📊 Symbol-Specific Amplification (COIN - SEC Crypto Rules):")
    coin_result = detector.detect_amplification(layer1_articles, layer2_articles, symbols=['COIN'])
    logger.info(f"   Has Amplification: {coin_result['has_amplification']}")
    logger.info(f"   Amplification Ratio: {coin_result['amplification_ratio']}")
    logger.info(f"   Layer 1: {coin_result['layer1_count']}, Layer 2: {coin_result['layer2_count']}")
    logger.info(f"   Amplification Level: {coin_result['amplification_level']}")
    logger.info(f"   Sentiment Shift: {coin_result['sentiment_shift']}")

    # 심볼별 증폭 감지 (Tesla - 낮은 증폭)
    logger.info("\n📊 Symbol-Specific Amplification (TSLA - Earnings):")
    tsla_result = detector.detect_amplification(layer1_articles, layer2_articles, symbols=['TSLA'])
    logger.info(f"   Has Amplification: {tsla_result['has_amplification']}")
    logger.info(f"   Amplification Ratio: {tsla_result['amplification_ratio']}")
    logger.info(f"   Layer 1: {tsla_result['layer1_count']}, Layer 2: {tsla_result['layer2_count']}")
    logger.info(f"   Amplification Level: {tsla_result['amplification_level']}")

    logger.info("\n" + "="*60)
    logger.info("✅ Amplification detection test completed!")
    logger.info("="*60)


if __name__ == "__main__":
    test_amplification()
