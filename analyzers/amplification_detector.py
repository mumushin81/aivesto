"""
여론 증폭 감지기 (Amplification Detector)
Layer 1 vs Layer 2 뉴스 비교를 통한 증폭 효과 탐지
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger


class AmplificationDetector:
    """
    여론 증폭 감지 시스템

    Layer 1 (Bloomberg, Reuters, WSJ) 뉴스가
    Layer 2 (Fox, CNN, Yahoo) 에서 얼마나 증폭되는지 탐지
    """

    def __init__(self, time_window_hours: int = 24):
        """
        Args:
            time_window_hours: 증폭 탐지 시간 윈도우 (기본 24시간)
        """
        self.time_window = timedelta(hours=time_window_hours)
        logger.info(f"AmplificationDetector initialized (window: {time_window_hours}h)")

    def detect_amplification(
        self,
        layer1_articles: List[Dict],
        layer2_articles: List[Dict],
        symbols: Optional[List[str]] = None
    ) -> Dict:
        """
        Layer 1 → Layer 2 증폭 효과 탐지

        Args:
            layer1_articles: Layer 1 뉴스 리스트 (Core Signal)
            layer2_articles: Layer 2 뉴스 리스트 (Sentiment & Momentum)
            symbols: 필터링할 심볼 리스트 (None이면 전체)

        Returns:
            {
                'has_amplification': True/False,
                'amplification_ratio': 5.2,  # Layer 2 / Layer 1
                'layer1_count': 3,
                'layer2_count': 16,
                'matched_topics': ['Federal Reserve rate hike', 'SEC regulation'],
                'sentiment_shift': 'neutral_to_negative',  # 감성 변화
                'amplification_level': 'high',  # low/medium/high/viral
                'details': {...}
            }
        """
        # 1. 심볼 필터링
        if symbols:
            layer1_articles = self._filter_by_symbols(layer1_articles, symbols)
            layer2_articles = self._filter_by_symbols(layer2_articles, symbols)

        # 2. 시간 필터링 (최근 time_window 내)
        layer1_recent = self._filter_by_time(layer1_articles, self.time_window)
        layer2_recent = self._filter_by_time(layer2_articles, self.time_window)

        layer1_count = len(layer1_recent)
        layer2_count = len(layer2_recent)

        # 3. 증폭 비율 계산
        if layer1_count == 0:
            return self._no_amplification_result()

        amplification_ratio = layer2_count / layer1_count

        # 4. 토픽 매칭 (키워드 기반)
        matched_topics = self._find_common_topics(layer1_recent, layer2_recent)

        # 5. 감성 변화 분석
        sentiment_shift = self._analyze_sentiment_shift(layer1_recent, layer2_recent)

        # 6. 증폭 레벨 결정
        amplification_level = self._calculate_amplification_level(
            amplification_ratio,
            len(matched_topics)
        )

        # 증폭 발생 조건: ratio > 2.0 또는 매칭된 토픽 > 2개
        has_amplification = (amplification_ratio > 2.0 or len(matched_topics) > 2)

        return {
            'has_amplification': has_amplification,
            'amplification_ratio': round(amplification_ratio, 2),
            'layer1_count': layer1_count,
            'layer2_count': layer2_count,
            'matched_topics': matched_topics,
            'sentiment_shift': sentiment_shift,
            'amplification_level': amplification_level,
            'details': {
                'layer1_sources': self._get_sources(layer1_recent),
                'layer2_sources': self._get_sources(layer2_recent),
                'time_window_hours': self.time_window.total_seconds() / 3600
            }
        }

    def _filter_by_symbols(self, articles: List[Dict], symbols: List[str]) -> List[Dict]:
        """심볼로 기사 필터링"""
        filtered = []
        for article in articles:
            article_symbols = article.get('symbols', [])
            if any(symbol in article_symbols for symbol in symbols):
                filtered.append(article)
        return filtered

    def _filter_by_time(self, articles: List[Dict], time_window: timedelta) -> List[Dict]:
        """시간 윈도우로 필터링"""
        now = datetime.now()
        cutoff_time = now - time_window

        filtered = []
        for article in articles:
            published_at = article.get('published_at')
            if isinstance(published_at, str):
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))

            if published_at and published_at >= cutoff_time:
                filtered.append(article)

        return filtered

    def _find_common_topics(self, layer1_articles: List[Dict], layer2_articles: List[Dict]) -> List[str]:
        """
        공통 토픽 찾기 (간단한 키워드 매칭)
        실제로는 TF-IDF, embedding 기반 유사도를 사용할 수 있음
        """
        # Layer 1 주요 키워드 추출
        layer1_keywords = set()
        for article in layer1_articles:
            title = article.get('title', '').lower()
            # 중요 키워드 추출 (3글자 이상 단어)
            words = [w for w in title.split() if len(w) > 3]
            layer1_keywords.update(words)

        # Layer 2에서 매칭되는 키워드 찾기
        matched_topics = set()
        for article in layer2_articles:
            title = article.get('title', '').lower()
            for keyword in layer1_keywords:
                if keyword in title:
                    matched_topics.add(keyword)

        return list(matched_topics)[:5]  # 최대 5개

    def _analyze_sentiment_shift(self, layer1_articles: List[Dict], layer2_articles: List[Dict]) -> str:
        """
        감성 변화 분석
        Layer 1 → Layer 2 감성이 어떻게 변했는지
        """
        # 평균 감성 계산
        layer1_sentiment = self._average_sentiment(layer1_articles)
        layer2_sentiment = self._average_sentiment(layer2_articles)

        # 감성 레이블
        def sentiment_label(score):
            if score > 0.1:
                return 'positive'
            elif score < -0.1:
                return 'negative'
            else:
                return 'neutral'

        l1_label = sentiment_label(layer1_sentiment)
        l2_label = sentiment_label(layer2_sentiment)

        if l1_label == l2_label:
            return f"{l1_label}_stable"
        else:
            return f"{l1_label}_to_{l2_label}"

    def _average_sentiment(self, articles: List[Dict]) -> float:
        """평균 감성 점수 (-1.0 ~ +1.0)"""
        if not articles:
            return 0.0

        scores = []
        for article in articles:
            metadata = article.get('metadata', {})
            sentiment_score = metadata.get('sentiment_score', 0.0)
            scores.append(sentiment_score)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_amplification_level(self, ratio: float, topic_count: int) -> str:
        """
        증폭 레벨 결정
        - viral: ratio > 10 or topic_count > 5
        - high: ratio > 5
        - medium: ratio > 2
        - low: ratio <= 2
        """
        if ratio > 10 or topic_count > 5:
            return 'viral'
        elif ratio > 5:
            return 'high'
        elif ratio > 2:
            return 'medium'
        else:
            return 'low'

    def _get_sources(self, articles: List[Dict]) -> List[str]:
        """기사 출처 리스트 추출"""
        sources = set()
        for article in articles:
            source = article.get('source', 'Unknown')
            sources.add(source)
        return list(sources)

    def _no_amplification_result(self) -> Dict:
        """증폭 없음 결과"""
        return {
            'has_amplification': False,
            'amplification_ratio': 0.0,
            'layer1_count': 0,
            'layer2_count': 0,
            'matched_topics': [],
            'sentiment_shift': 'none',
            'amplification_level': 'none',
            'details': {}
        }

    def track_amplification_over_time(
        self,
        symbol: str,
        layer1_articles: List[Dict],
        layer2_articles: List[Dict],
        interval_hours: int = 6
    ) -> List[Dict]:
        """
        시간별 증폭 추이 추적

        Args:
            symbol: 추적할 심볼
            layer1_articles: Layer 1 기사
            layer2_articles: Layer 2 기사
            interval_hours: 추적 간격 (기본 6시간)

        Returns:
            시간별 증폭 데이터 리스트
        """
        results = []
        now = datetime.now()

        # 지난 24시간을 6시간 간격으로 분할
        for i in range(4):  # 24h / 6h = 4 intervals
            end_time = now - timedelta(hours=i * interval_hours)
            start_time = end_time - timedelta(hours=interval_hours)

            # 해당 시간대 기사 필터링
            l1_filtered = [
                a for a in layer1_articles
                if start_time <= self._get_published_time(a) < end_time
                   and symbol in a.get('symbols', [])
            ]

            l2_filtered = [
                a for a in layer2_articles
                if start_time <= self._get_published_time(a) < end_time
                   and symbol in a.get('symbols', [])
            ]

            # 증폭 탐지
            result = self.detect_amplification(l1_filtered, l2_filtered, [symbol])
            result['time_period'] = {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            }

            results.append(result)

        return results

    def _get_published_time(self, article: Dict) -> datetime:
        """기사 발행 시간 추출"""
        published_at = article.get('published_at')
        if isinstance(published_at, str):
            return datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        return published_at or datetime.min
