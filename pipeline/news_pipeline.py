"""
엔드투엔드 뉴스 수집 및 분석 파이프라인
Layer 1/2 수집 → NER → Sentiment → Policy → Amplification → Supabase
"""
import sys
sys.path.append('..')

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

# Collectors
from collectors.bloomberg_collector import BloombergCollector
from collectors.reuters_collector import ReutersCollector
from collectors.wsj_collector import WSJCollector
from collectors.fox_collector import FoxCollector
from collectors.cnn_collector import CNNCollector
from collectors.yahoo_collector import YahooCollector

# Analyzers
from analyzers.ner_extractor import NERExtractor
from analyzers.sentiment_analyzer import SentimentAnalyzer
from analyzers.policy_detector import PolicyDetector
from analyzers.amplification_detector import AmplificationDetector

# Database
from database.supabase_client import SupabaseClient
from database.models import RawNews


class NewsPipeline:
    """
    전체 뉴스 수집 및 분석 파이프라인

    워크플로우:
    1. Layer 1 수집 (Bloomberg, Reuters, WSJ)
    2. Layer 2 수집 (Fox, CNN, Yahoo)
    3. NER 추출 (종목 심볼)
    4. Sentiment 분석 (VADER)
    5. Policy 감지 (정책 변화)
    6. Amplification 감지 (Layer 1→2 증폭)
    7. Supabase 저장
    """

    def __init__(self, db_client: Optional[SupabaseClient] = None, use_finbert: bool = False):
        """
        Args:
            db_client: Supabase 클라이언트 (None이면 저장만 안 함, 수집은 진행)
            use_finbert: FinBERT 사용 여부 (느리지만 정확)
        """
        self.db = db_client

        # 더미 DB 클라이언트 (수집기 초기화용)
        dummy_db = db_client if db_client else type('DummyDB', (), {})()

        # Layer 1 수집기 (항상 초기화)
        self.layer1_collectors = [
            BloombergCollector(dummy_db),
            ReutersCollector(dummy_db),
            WSJCollector(dummy_db)
        ]

        # Layer 2 수집기 (항상 초기화)
        self.layer2_collectors = [
            FoxCollector(dummy_db),
            CNNCollector(dummy_db),
            YahooCollector(dummy_db)
        ]

        # 분석 엔진
        self.ner = NERExtractor(use_spacy=False)  # Regex만 (빠름)
        self.sentiment = SentimentAnalyzer(use_finbert=use_finbert)
        self.policy = PolicyDetector()
        self.amplification = AmplificationDetector(time_window_hours=24)

        logger.info("NewsPipeline initialized")
        logger.info(f"  Layer 1 collectors: {len(self.layer1_collectors)}")
        logger.info(f"  Layer 2 collectors: {len(self.layer2_collectors)}")
        logger.info(f"  FinBERT enabled: {use_finbert}")

    def run(self, save_to_db: bool = True) -> Dict:
        """
        전체 파이프라인 실행

        Returns:
            {
                'layer1_articles': [...],
                'layer2_articles': [...],
                'analyzed_articles': [...],
                'amplification_results': {...},
                'stats': {...}
            }
        """
        logger.info("\n" + "="*60)
        logger.info("🚀 Starting News Pipeline")
        logger.info("="*60)

        start_time = datetime.now()

        # 1. Layer 1 수집
        layer1_articles = self._collect_layer1()
        logger.info(f"✅ Layer 1 collected: {len(layer1_articles)} articles")

        # 2. Layer 2 수집
        layer2_articles = self._collect_layer2()
        logger.info(f"✅ Layer 2 collected: {len(layer2_articles)} articles")

        # 3. 분석 파이프라인 (Layer 1 + Layer 2)
        all_articles = layer1_articles + layer2_articles
        analyzed_articles = self._analyze_articles(all_articles)
        logger.info(f"✅ Analysis complete: {len(analyzed_articles)} articles")

        # 4. 증폭 감지
        amplification_results = self._detect_amplification(
            layer1_articles,
            layer2_articles,
            analyzed_articles
        )
        logger.info(f"✅ Amplification detection complete")

        # 5. Supabase 저장
        saved_count = 0
        if save_to_db and self.db:
            saved_count = self._save_to_database(analyzed_articles)
            logger.info(f"✅ Saved to Supabase: {saved_count} articles")

        # 통계
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        stats = {
            'total_articles': len(all_articles),
            'layer1_count': len(layer1_articles),
            'layer2_count': len(layer2_articles),
            'analyzed_count': len(analyzed_articles),
            'saved_count': saved_count,
            'high_priority_count': sum(1 for a in analyzed_articles if a.get('priority_score', 0) >= 80),
            'policy_signals': sum(1 for a in analyzed_articles if a.get('has_policy', False)),
            'amplification_detected': amplification_results.get('has_amplification', False),
            'duration_seconds': round(duration, 2)
        }

        logger.info("\n" + "="*60)
        logger.info("📊 Pipeline Stats:")
        logger.info(f"  Total Articles: {stats['total_articles']}")
        logger.info(f"  Layer 1: {stats['layer1_count']}, Layer 2: {stats['layer2_count']}")
        logger.info(f"  High Priority (80+): {stats['high_priority_count']}")
        logger.info(f"  Policy Signals: {stats['policy_signals']}")
        logger.info(f"  Amplification: {stats['amplification_detected']}")
        logger.info(f"  Saved to DB: {stats['saved_count']}")
        logger.info(f"  Duration: {stats['duration_seconds']}s")
        logger.info("="*60)

        return {
            'layer1_articles': layer1_articles,
            'layer2_articles': layer2_articles,
            'analyzed_articles': analyzed_articles,
            'amplification_results': amplification_results,
            'stats': stats
        }

    def _collect_layer1(self) -> List[RawNews]:
        """Layer 1 수집 (Core Signal)"""
        logger.info("\n📰 Collecting Layer 1 (Bloomberg, Reuters, WSJ)...")
        all_articles = []

        for collector in self.layer1_collectors:
            try:
                articles = collector.fetch_news()
                all_articles.extend(articles)
                logger.info(f"  {collector.source_name}: {len(articles)}")
            except Exception as e:
                logger.error(f"  ❌ {collector.source_name} failed: {e}")

        return all_articles

    def _collect_layer2(self) -> List[RawNews]:
        """Layer 2 수집 (Sentiment & Momentum)"""
        logger.info("\n📺 Collecting Layer 2 (Fox, CNN, Yahoo)...")
        all_articles = []

        for collector in self.layer2_collectors:
            try:
                articles = collector.fetch_news()
                all_articles.extend(articles)
                logger.info(f"  {collector.source_name}: {len(articles)}")
            except Exception as e:
                logger.error(f"  ❌ {collector.source_name} failed: {e}")

        return all_articles

    def _analyze_articles(self, articles: List[RawNews]) -> List[Dict]:
        """기사 분석 (NER, Sentiment, Policy)"""
        logger.info("\n🔬 Analyzing articles...")
        analyzed = []

        for article in articles:
            try:
                # 텍스트 준비
                text = f"{article.title} {article.content or ''}"

                # 1. NER (종목 심볼 추출)
                symbols = self.ner.extract_symbols(text)

                # 2. Sentiment (감성 분석)
                sentiment_result = self.sentiment.analyze(text, method='vader')

                # 3. Policy (정책 감지)
                policy_result = self.policy.detect(text)

                # 4. Priority Score 계산
                priority_score = self._calculate_priority_score(
                    sentiment_result,
                    policy_result,
                    len(symbols)
                )

                # 결과 저장
                analyzed_article = {
                    'raw_news': article,
                    'symbols': symbols,
                    'sentiment': sentiment_result['sentiment'],
                    'sentiment_score': sentiment_result['score'],
                    'has_policy': policy_result['has_policy_change'],
                    'policy_type': policy_result['change_type'],
                    'policy_description': policy_result.get('policy_description', ''),
                    'priority_score': priority_score,
                    'analyzed_at': datetime.now().isoformat()
                }

                analyzed.append(analyzed_article)

            except Exception as e:
                logger.warning(f"  Analysis failed for article: {e}")

        return analyzed

    def _calculate_priority_score(
        self,
        sentiment: Dict,
        policy: Dict,
        symbol_count: int
    ) -> int:
        """
        우선순위 점수 계산 (0-100)

        - 정책 변화: 90-100
        - 강한 감성 (|score| > 0.5): +30
        - 여러 심볼 언급: +10
        """
        score = 50  # 기본

        # 정책 변화 (최우선)
        if policy.get('has_policy_change'):
            if policy['change_type'] == 'new_policy':
                score = 95
            elif policy['change_type'] == 'policy_removed':
                score = 95
            elif policy['change_type'] == 'policy_changed':
                score = 90

        # 감성 강도
        sentiment_score = abs(sentiment.get('score', 0))
        if sentiment_score > 0.5:
            score += 30
        elif sentiment_score > 0.3:
            score += 20
        elif sentiment_score > 0.1:
            score += 10

        # 심볼 수
        if symbol_count > 0:
            score += min(symbol_count * 5, 20)

        return min(score, 100)

    def _detect_amplification(
        self,
        layer1_articles: List,
        layer2_articles: List,
        analyzed_articles: List
    ) -> Dict:
        """증폭 감지"""
        logger.info("\n🔊 Detecting amplification...")

        # RawNews → Dict 변환
        layer1_dict = [self._raw_news_to_dict(a) for a in layer1_articles]
        layer2_dict = [self._raw_news_to_dict(a) for a in layer2_articles]

        # 전체 증폭 감지
        result = self.amplification.detect_amplification(layer1_dict, layer2_dict)

        logger.info(f"  Amplification Ratio: {result['amplification_ratio']}")
        logger.info(f"  Amplification Level: {result['amplification_level']}")

        return result

    def _raw_news_to_dict(self, raw_news: RawNews) -> Dict:
        """RawNews → Dict 변환"""
        return {
            'title': raw_news.title,
            'source': raw_news.source,
            'symbols': raw_news.symbols or [],
            'published_at': raw_news.published_at.isoformat() if raw_news.published_at else None,
            'metadata': raw_news.metadata or {}
        }

    def _save_to_database(self, analyzed_articles: List[Dict]) -> int:
        """Supabase 저장"""
        if not self.db:
            return 0

        saved_count = 0
        for article in analyzed_articles:
            try:
                raw_news = article['raw_news']

                # 중복 확인
                existing = self.db.get_raw_news_by_url(raw_news.url)
                if existing:
                    continue

                # 저장
                news_id = self.db.insert_raw_news(raw_news)
                if news_id:
                    saved_count += 1

            except Exception as e:
                logger.warning(f"  Failed to save article: {e}")

        return saved_count
