#!/usr/bin/env python3
"""
Phase 2 분석기 테스트
NER, 감성 분석, 정책 감지
"""
from analyzers.ner_extractor import NERExtractor
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.policy_detector import PolicyDetector
from loguru import logger


def test_ner():
    """NER 테스트"""
    logger.info("\n" + "="*60)
    logger.info("🔍 Testing NER Extractor")
    logger.info("="*60)

    ner = NERExtractor(use_spacy=False)  # Regex만 (spaCy 미설치)

    test_texts = [
        "Apple (AAPL) and Microsoft (MSFT) announced partnership",
        "Tesla CEO Elon Musk tweeted about $TSLA stock",
        "NASDAQ:NVDA surged after earnings beat",
        "Goldman Sachs upgraded Amazon to buy"
    ]

    for text in test_texts:
        symbols = ner.extract_symbols(text)
        logger.info(f"Text: {text}")
        logger.info(f"   → Symbols: {symbols}\n")


def test_sentiment():
    """감성 분석 테스트"""
    logger.info("\n" + "="*60)
    logger.info("😊 Testing Sentiment Analyzer")
    logger.info("="*60)

    sentiment = SentimentAnalyzer(use_finbert=False)  # VADER만

    test_texts = [
        "Apple reported record-breaking quarterly earnings, beating analyst expectations.",
        "Tesla stock plummeted after CEO resignation rumors.",
        "Microsoft announced new product line.",
        "The company faces serious regulatory challenges and potential fines."
    ]

    for text in test_texts:
        result = sentiment.analyze(text, method='vader')
        logger.info(f"Text: {text[:60]}...")
        logger.info(f"   → Sentiment: {result['sentiment']} ({result['score']:.2f})\n")


def test_policy():
    """정책 감지 테스트"""
    logger.info("\n" + "="*60)
    logger.info("🏛️  Testing Policy Detector")
    logger.info("="*60)

    detector = PolicyDetector()

    test_texts = [
        "The SEC introduces new regulation on cryptocurrency trading platforms",
        "Congress repeals the tech antitrust bill after industry pressure",
        "Federal Reserve raises interest rate by 0.25% to combat inflation",
        "Apple launches new iPhone 15 with improved camera",  # 정책 무관
        "FDA approves Moderna's new COVID-19 vaccine for emergency use"
    ]

    for text in test_texts:
        result = detector.detect(text)
        logger.info(f"Text: {text[:60]}...")
        logger.info(f"   → Has Policy: {result['has_policy_change']}")
        if result['has_policy_change']:
            logger.info(f"   → Type: {result['change_type']}")
            logger.info(f"   → Sectors: {result['affected_sectors']}")
            logger.info(f"   → Confidence: {result['confidence']:.2f}")
        logger.info("")


def test_integrated():
    """통합 테스트 - 실제 뉴스"""
    logger.info("\n" + "="*60)
    logger.info("🔬 Integrated Test - Real News Analysis")
    logger.info("="*60)

    ner = NERExtractor(use_spacy=False)
    sentiment = SentimentAnalyzer(use_finbert=False)
    detector = PolicyDetector()

    news_article = """
    Wall Street Banks Prepare to Sell Billions of Dollars of X Loans.

    Several major banks including Goldman Sachs and Morgan Stanley are preparing
    to sell billions of dollars in loans used to fund Elon Musk's acquisition of
    Twitter, now called X. The banks have been holding these loans on their books
    for over a year, facing potential losses. This move could impact both the
    banks' quarterly earnings and X's financial position.
    """

    logger.info(f"Article: {news_article[:100]}...\n")

    # NER
    symbols = ner.extract_symbols(news_article)
    logger.info(f"📊 Extracted Symbols: {symbols}")

    # Sentiment
    sent_result = sentiment.analyze(news_article, method='vader')
    logger.info(f"😊 Sentiment: {sent_result['sentiment']} (score: {sent_result['score']:.2f})")

    # Policy
    policy_result = detector.detect(news_article)
    logger.info(f"🏛️  Policy Change: {policy_result['has_policy_change']}")

    logger.info("\n" + "="*60)
    logger.info("✅ All tests completed!")
    logger.info("="*60)


if __name__ == "__main__":
    test_ner()
    test_sentiment()
    test_policy()
    test_integrated()
