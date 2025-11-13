"""
투자 시그널 대시보드 API
Investment Signal Dashboard API
"""

import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger

sys.path.append('..')
from database.supabase_client import SupabaseClient


class SignalAPI:
    """투자 시그널 API"""

    def __init__(self):
        self.db = SupabaseClient()
        logger.info("Signal API initialized")

    def get_signals_by_level(
        self,
        level: int,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """레벨별 시그널 조회

        Args:
            level: 신호 레벨 (1-4)
            hours: 최근 N시간 데이터
            limit: 최대 개수

        Returns:
            신호 리스트
        """
        try:
            # Supabase 쿼리로 데이터 조회
            # 실제 구현은 database 연결에 따라 수정 필요
            signals = self.db.get_signals_by_level(level, hours=hours, limit=limit)
            logger.info(f"Fetched {len(signals)} Level {level} signals")
            return signals

        except Exception as e:
            logger.error(f"Error fetching signals by level: {e}")
            return []

    def get_urgent_signals(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """긴급 시그널 (Level 1) 조회"""
        return self.get_signals_by_level(1, hours=hours, limit=limit)

    def get_high_priority_signals(self, hours: int = 24, limit: int = 30) -> List[Dict]:
        """높은 우선순위 시그널 (Level 1-2) 조회"""
        signals = []
        signals.extend(self.get_signals_by_level(1, hours=hours, limit=limit))
        signals.extend(self.get_signals_by_level(2, hours=hours, limit=limit))
        return signals

    def get_signals_by_symbol(
        self,
        symbol: str,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict]:
        """종목별 시그널 조회"""
        try:
            signals = self.db.get_signals_by_symbol(symbol, hours=hours, limit=limit)
            logger.info(f"Fetched {len(signals)} signals for {symbol}")
            return signals

        except Exception as e:
            logger.error(f"Error fetching signals for {symbol}: {e}")
            return []

    def get_trending_symbols(self, hours: int = 24, limit: int = 15) -> List[Dict]:
        """트렌딩 종목 조회 (가장 많은 시그널 나온 종목)"""
        try:
            symbols = self.db.get_trending_symbols(hours=hours, limit=limit)
            logger.info(f"Fetched {len(symbols)} trending symbols")
            return symbols

        except Exception as e:
            logger.error(f"Error fetching trending symbols: {e}")
            return []

    def get_dashboard_summary(self, hours: int = 24) -> Dict:
        """대시보드 요약 정보"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "period_hours": hours,
                "urgent_count": len(self.get_signals_by_level(1, hours=hours)),
                "high_count": len(self.get_signals_by_level(2, hours=hours)),
                "medium_count": len(self.get_signals_by_level(3, hours=hours)),
                "low_count": len(self.get_signals_by_level(4, hours=hours)),
                "trending_symbols": self.get_trending_symbols(hours=hours, limit=10),
                "latest_signals": self.get_signals_by_level(1, hours=hours, limit=5)
            }

        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return {}

    def get_price_impact_summary(self, hours: int = 24) -> Dict:
        """가격 영향 요약"""
        try:
            # 양수/음수/중립 시그널 비율 계산
            return self.db.get_price_impact_summary(hours=hours)

        except Exception as e:
            logger.error(f"Error getting price impact summary: {e}")
            return {"up": 0, "down": 0, "neutral": 0}

    def get_important_symbols_today(self) -> List[Dict]:
        """오늘 주목할 종목"""
        try:
            return self.db.get_important_symbols_today()

        except Exception as e:
            logger.error(f"Error getting important symbols: {e}")
            return []

    def mark_signal_as_processed(self, signal_id: str) -> bool:
        """시그널을 처리됨으로 표시"""
        try:
            # 이 기능은 블로거 큐에서 선택한 시그널을 표시
            return self.db.mark_signal_as_processed(signal_id)

        except Exception as e:
            logger.error(f"Error marking signal as processed: {e}")
            return False

    def get_signals_for_article(
        self,
        tier: str = "tier_1",
        hours: int = 24
    ) -> List[Dict]:
        """글 작성용 시그널 조회"""
        try:
            if tier == "tier_1":
                # 긴급 + 높음 시그널만
                signals = self.get_signals_by_level(1, hours=hours, limit=30)
                signals.extend(self.get_signals_by_level(2, hours=hours, limit=20))
            elif tier == "tier_2":
                # 높음 + 중간 시그널
                signals = self.get_signals_by_level(2, hours=hours, limit=30)
                signals.extend(self.get_signals_by_level(3, hours=hours, limit=20))
            else:  # tier_3
                # 모든 시그널
                signals = []
                for level in [1, 2, 3, 4]:
                    signals.extend(self.get_signals_by_level(level, hours=hours*7, limit=50))

            return signals

        except Exception as e:
            logger.error(f"Error getting signals for article: {e}")
            return []
