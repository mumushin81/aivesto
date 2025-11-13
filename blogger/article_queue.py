"""
블로거 글쓰기 큐 시스템
Blogger Article Queue System
"""

import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
from loguru import logger

sys.path.append('..')
from database.supabase_client import SupabaseClient
from dashboard.signal_api import SignalAPI


class QueueStatus(Enum):
    """큐 항목 상태"""
    PENDING = "pending"  # 대기 중
    SELECTED = "selected"  # 선택됨
    WRITING = "writing"  # 작성 중
    PUBLISHED = "published"  # 발행됨
    SKIPPED = "skipped"  # 스킵됨


class ArticleQueueManager:
    """블로거 글쓰기 큐 관리자"""

    def __init__(self):
        self.db = SupabaseClient()
        self.signal_api = SignalAPI()
        logger.info("Article queue manager initialized")

    def get_recommended_signals(self, tier: str = "tier_1", hours: int = 24,
                               limit: int = 30) -> List[Dict]:
        """
        글 작성 추천 시그널 조회

        Args:
            tier: 글 등급 (tier_1, tier_2, tier_3)
            hours: 최근 N시간
            limit: 최대 개수

        Returns:
            추천 시그널 리스트
        """
        try:
            logger.info(f"Getting recommended signals for {tier}")

            if tier == "tier_1":
                # Tier 1: 긴급 + 높음 시그널만 (Level 1-2)
                signals = self.signal_api.get_signals_by_level(1, hours=hours, limit=limit)
                signals.extend(self.signal_api.get_signals_by_level(2, hours=hours, limit=limit//2))
            elif tier == "tier_2":
                # Tier 2: 높음 + 중간 시그널 (Level 2-3)
                signals = self.signal_api.get_signals_by_level(2, hours=hours, limit=limit)
                signals.extend(self.signal_api.get_signals_by_level(3, hours=hours, limit=limit//2))
            else:  # tier_3
                # Tier 3: 모든 시그널 (확장된 기간)
                signals = []
                for level in [1, 2, 3, 4]:
                    signals.extend(self.signal_api.get_signals_by_level(
                        level, hours=hours*7, limit=limit//4
                    ))

            # 이미 발행된 신호 제외
            published_ids = self._get_published_signal_ids()
            new_signals = [s for s in signals if s.get('id') not in published_ids]

            logger.info(f"Found {len(new_signals)} new recommendations for {tier}")
            return new_signals[:limit]

        except Exception as e:
            logger.error(f"Error getting recommended signals: {e}")
            return []

    def get_queue_status(self, tier: str = "tier_1") -> Dict:
        """
        현재 큐 상태 조회

        Returns:
            pending, selected, writing, published 개수
        """
        try:
            recommendations = self.get_recommended_signals(tier, limit=100)
            trending = self.signal_api.get_trending_symbols(limit=10)

            return {
                "tier": tier,
                "timestamp": datetime.now().isoformat(),
                "queue": {
                    "pending": len(recommendations),
                    "trending_symbols": len(trending),
                    "top_trending": trending[:3]
                },
                "recommendations": recommendations[:10]
            }

        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {}

    def get_by_symbol(self, symbol: str, tier: str = "tier_1",
                     hours: int = 24, limit: int = 10) -> List[Dict]:
        """
        특정 종목의 글쓰기 신호 조회
        """
        try:
            signals = self.signal_api.get_signals_by_symbol(symbol, hours=hours, limit=limit)
            published_ids = self._get_published_signal_ids()
            new_signals = [s for s in signals if s.get('id') not in published_ids]

            logger.info(f"Found {len(new_signals)} unpublished signals for {symbol}")
            return new_signals

        except Exception as e:
            logger.error(f"Error getting signals for symbol: {e}")
            return []

    def get_urgent_recommendations(self) -> List[Dict]:
        """긴급 추천 (Level 1 신호만)"""
        try:
            signals = self.signal_api.get_urgent_signals(hours=24, limit=20)
            published_ids = self._get_published_signal_ids()
            new_signals = [s for s in signals if s.get('id') not in published_ids]

            logger.info(f"Found {len(new_signals)} urgent recommendations")
            return new_signals

        except Exception as e:
            logger.error(f"Error getting urgent recommendations: {e}")
            return []

    def get_daily_article_suggestions(self) -> List[Dict]:
        """오늘 작성할 글 제안"""
        try:
            # 오늘 주목할 종목에서 신호 수집
            important_symbols = self.signal_api.get_important_symbols_today()

            suggestions = []
            for symbol_info in important_symbols[:5]:
                symbol = symbol_info['symbol']
                signals = self.get_by_symbol(symbol, limit=3)
                if signals:
                    suggestions.append({
                        "symbol": symbol,
                        "urgent_count": symbol_info.get('urgent_count', 0),
                        "signal_count": symbol_info.get('signals', 0),
                        "sample_signals": signals[:2]
                    })

            logger.info(f"Generated {len(suggestions)} daily article suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"Error generating daily suggestions: {e}")
            return []

    def mark_signal_queued(self, signal_id: str, article_tier: str) -> bool:
        """신호를 글 작성 큐에 추가"""
        try:
            # 향후 구현: queue_history 테이블에 기록
            logger.info(f"Marked signal {signal_id} for {article_tier}")
            return True

        except Exception as e:
            logger.error(f"Error marking signal queued: {e}")
            return False

    def mark_signal_published(self, signal_id: str, article_id: str) -> bool:
        """신호를 발행됨으로 표시"""
        try:
            # 향후 구현: queue_history 또는 analyzed_news 테이블 업데이트
            logger.info(f"Marked signal {signal_id} as published in article {article_id}")
            return True

        except Exception as e:
            logger.error(f"Error marking signal published: {e}")
            return False

    def _get_published_signal_ids(self) -> set:
        """이미 발행된 신호 ID 목록"""
        try:
            result = self.db.client.table("published_articles")\
                .select("analyzed_news_ids")\
                .execute()

            all_ids = set()
            for item in result.data:
                all_ids.update(item.get("analyzed_news_ids", []))

            return all_ids

        except Exception as e:
            logger.error(f"Error getting published signal IDs: {e}")
            return set()

    def get_statistics(self) -> Dict:
        """큐 통계 조회"""
        try:
            # 최근 7일간 데이터
            cutoff_time = (datetime.now() - timedelta(days=7)).isoformat()

            # 분석된 신호
            analyzed = self.db.client.table("analyzed_news")\
                .select("count()", method="count")\
                .gte("created_at", cutoff_time)\
                .execute()

            # 발행된 글
            published = self.db.client.table("published_articles")\
                .select("count()", method="count")\
                .gte("created_at", cutoff_time)\
                .execute()

            return {
                "period_days": 7,
                "analyzed_signals": analyzed.count if hasattr(analyzed, 'count') else 0,
                "published_articles": published.count if hasattr(published, 'count') else 0,
                "conversion_rate": "N/A"  # 향후 계산
            }

        except Exception as e:
            logger.error(f"Error getting queue statistics: {e}")
            return {}

    def get_smart_recommendations(self) -> Dict:
        """스마트 추천 (다양한 관점)"""
        try:
            recommendations = {
                "timestamp": datetime.now().isoformat(),
                "tier_1_urgent": self.get_urgent_recommendations(),
                "daily_suggestions": self.get_daily_article_suggestions(),
                "trending_symbols": self.signal_api.get_trending_symbols(limit=10),
                "queue_summary": {
                    "tier_1_pending": len(self.get_recommended_signals("tier_1", limit=50)),
                    "tier_2_pending": len(self.get_recommended_signals("tier_2", limit=50)),
                    "tier_3_pending": len(self.get_recommended_signals("tier_3", limit=100))
                }
            }

            logger.info("Generated smart recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating smart recommendations: {e}")
            return {}
