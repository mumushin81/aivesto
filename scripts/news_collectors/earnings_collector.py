#!/usr/bin/env python3
"""
실적(Earnings) 뉴스 수집기

수집 대상:
- Earnings Release
- Earnings Call Transcript
- EPS, Revenue 서프라이즈/쇼크
- 가이던스 상향/하향
- 애널리스트 Target Price 변경

데이터 소스:
- Yahoo Finance API
- Alpha Vantage Earnings API
- FMP (Financial Modeling Prep) API
- Seeking Alpha (Premium)
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from typing import List, Dict, Any
import yfinance as yf

load_dotenv()


class EarningsNewsCollector:
    """실적 뉴스 수집기"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        # API Keys
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.fmp_key = os.getenv("FMP_API_KEY")  # Financial Modeling Prep

        # 추적할 종목
        self.tracked_symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "NFLX", "ADBE", "UBER"
        ]

    def collect_earnings_calendar(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        향후 실적 발표 일정 수집
        Source: Alpha Vantage Earnings Calendar
        """
        logger.info(f"📊 실적 발표 일정 수집 중 ({days_ahead}일)...")

        if not self.alpha_vantage_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set")
            return []

        try:
            earnings_calendar = []

            for symbol in self.tracked_symbols:
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "EARNINGS_CALENDAR",
                    "symbol": symbol,
                    "apikey": self.alpha_vantage_key
                }

                response = requests.get(url, params=params)
                response.raise_for_status()

                # CSV 파싱
                lines = response.text.strip().split('\n')
                if len(lines) > 1:
                    headers = lines[0].split(',')
                    for line in lines[1:]:
                        values = line.split(',')
                        if len(values) == len(headers):
                            earnings_calendar.append({
                                "symbol": symbol,
                                "report_date": values[0],
                                "fiscal_period": values[1] if len(values) > 1 else None,
                                "estimate": float(values[2]) if len(values) > 2 and values[2] else None
                            })

            logger.success(f"  ✅ 실적 일정 {len(earnings_calendar)}개 수집 완료")
            return earnings_calendar

        except Exception as e:
            logger.error(f"  ❌ 실적 일정 수집 실패: {e}")
            return []

    def collect_earnings_data(self, symbol: str) -> Dict[str, Any]:
        """
        특정 종목의 최근 실적 데이터 수집
        Source: yfinance
        """
        logger.info(f"📊 {symbol} 실적 데이터 수집 중...")

        try:
            stock = yf.Ticker(symbol)

            # 실적 데이터
            earnings = stock.earnings
            quarterly_earnings = stock.quarterly_earnings

            if quarterly_earnings is None or quarterly_earnings.empty:
                logger.warning(f"  ⚠️  {symbol}: 실적 데이터 없음")
                return {}

            # 최근 분기 데이터
            latest_quarter = quarterly_earnings.iloc[0]

            earnings_data = {
                "symbol": symbol,
                "quarter": latest_quarter.name if hasattr(latest_quarter, 'name') else "Unknown",
                "revenue": float(latest_quarter.get('Revenue', 0)),
                "earnings": float(latest_quarter.get('Earnings', 0)),
                "collected_at": datetime.now().isoformat()
            }

            logger.success(f"  ✅ {symbol} 실적 데이터 수집 완료")
            return earnings_data

        except Exception as e:
            logger.error(f"  ❌ {symbol} 실적 수집 실패: {e}")
            return {}

    def collect_analyst_ratings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        애널리스트 목표가 및 등급 변경 수집
        Source: FMP API
        """
        logger.info(f"📊 {symbol} 애널리스트 리포트 수집 중...")

        if not self.fmp_key:
            logger.warning("FMP_API_KEY not set")
            return []

        try:
            url = f"https://financialmodelingprep.com/api/v3/analyst-stock-recommendations/{symbol}"
            params = {"apikey": self.fmp_key}

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            analyst_ratings = []
            for rating in data[:10]:  # 최근 10개
                analyst_ratings.append({
                    "symbol": symbol,
                    "analyst": rating.get("analystCompany", "Unknown"),
                    "rating": rating.get("analystRating", ""),
                    "target_price": float(rating.get("targetPrice", 0)),
                    "date": rating.get("date", "")
                })

            logger.success(f"  ✅ {symbol} 애널리스트 {len(analyst_ratings)}개 수집 완료")
            return analyst_ratings

        except Exception as e:
            logger.error(f"  ❌ {symbol} 애널리스트 리포트 실패: {e}")
            return []

    def analyze_earnings_signal(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        실적 데이터에서 시그널 분석

        시그널 포인트:
        - EPS/매출 서프라이즈 → 단기 모멘텀
        - 가이던스 상향 → 중기 상승
        - 목표가 상향 → 강한 중기 시그널
        """

        symbol = earnings_data.get("symbol")
        eps_actual = earnings_data.get("eps_actual", 0)
        eps_consensus = earnings_data.get("eps_consensus", 0)
        revenue_actual = earnings_data.get("revenue_actual", 0)
        revenue_consensus = earnings_data.get("revenue_consensus", 0)

        signal = {
            "symbol": symbol,
            "signal": None,
            "strength": "NEUTRAL",
            "expected_move": "0%"
        }

        # EPS 서프라이즈
        eps_surprise = ((eps_actual - eps_consensus) / eps_consensus * 100) if eps_consensus else 0

        # Revenue 서프라이즈
        revenue_surprise = ((revenue_actual - revenue_consensus) / revenue_consensus * 100) if revenue_consensus else 0

        # 시그널 판단
        if eps_surprise > 5 and revenue_surprise > 5:
            signal["signal"] = "STRONG_BUY"
            signal["strength"] = "HIGH"
            signal["expected_move"] = "+3% avg"

        elif eps_surprise > 0 and revenue_surprise > 0:
            signal["signal"] = "BUY"
            signal["strength"] = "MEDIUM"
            signal["expected_move"] = "+1.5% avg"

        elif eps_surprise < -5 or revenue_surprise < -5:
            signal["signal"] = "STRONG_SELL"
            signal["strength"] = "HIGH"
            signal["expected_move"] = "-3% avg"

        return signal

    def save_to_database(self, data: List[Dict[str, Any]], data_type: str):
        """수집한 데이터를 Supabase에 저장"""

        logger.info(f"💾 {data_type} Supabase에 저장 중...")

        for item in data:
            try:
                if data_type == "earnings":
                    result = self.supabase.table('earnings_news').insert({
                        "symbol": item.get("symbol"),
                        "quarter": item.get("quarter"),
                        "eps_actual": item.get("eps_actual"),
                        "eps_consensus": item.get("eps_consensus"),
                        "revenue_actual": item.get("revenue_actual"),
                        "revenue_consensus": item.get("revenue_consensus"),
                        "guidance": item.get("guidance", "MAINTAIN"),
                        "signal_strength": item.get("signal_strength", "NEUTRAL")
                    }).execute()

                logger.success(f"  ✅ {item.get('symbol')} 저장 완료")

            except Exception as e:
                logger.error(f"  ❌ 저장 실패: {e}")

    def run(self):
        """실적 뉴스 수집 실행"""

        logger.info("=" * 60)
        logger.info("🚀 실적 뉴스 수집 시작")
        logger.info("=" * 60)

        all_earnings = []
        all_ratings = []

        # 1. 실적 발표 일정
        earnings_calendar = self.collect_earnings_calendar()

        # 2. 각 종목별 실적 데이터
        for symbol in self.tracked_symbols:
            earnings_data = self.collect_earnings_data(symbol)
            if earnings_data:
                all_earnings.append(earnings_data)

        # 3. 애널리스트 리포트
        for symbol in self.tracked_symbols[:3]:  # 테스트: 3개만
            ratings = self.collect_analyst_ratings(symbol)
            all_ratings.extend(ratings)

        # 4. 데이터베이스 저장
        if all_earnings:
            self.save_to_database(all_earnings, "earnings")

        logger.info("\n" + "=" * 60)
        logger.success(f"✅ 실적 데이터 수집 완료: {len(all_earnings)}개")
        logger.success(f"✅ 애널리스트 리포트: {len(all_ratings)}개")
        logger.info("=" * 60)

        return {
            "calendar": earnings_calendar,
            "earnings": all_earnings,
            "ratings": all_ratings
        }


def main():
    """메인 함수"""
    collector = EarningsNewsCollector()
    result = collector.run()


if __name__ == "__main__":
    main()
