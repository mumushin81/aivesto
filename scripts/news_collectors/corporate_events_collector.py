#!/usr/bin/env python3
"""
기업 PR + 사고/이슈성 뉴스 수집기

수집 대상:
- M&A 발표
- SEC 조사, 소송
- CEO 교체
- 제품 출시/리콜
- 파산 신청/자금조달
- 내부자 매매 (Insider Trading)

데이터 소스:
- SEC EDGAR API (8-K, 10-K 필링)
- BusinessWire
- GlobeNewswire
- Reuters Company News
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from typing import List, Dict, Any

load_dotenv()


class CorporateEventsCollector:
    """기업 이슈 뉴스 수집기"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        self.fmp_key = os.getenv("FMP_API_KEY")

        # 추적할 종목
        self.tracked_symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "NFLX", "ADBE", "UBER"
        ]

    def collect_sec_filings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        SEC 필링 수집 (8-K, 10-K, 10-Q)
        Source: SEC EDGAR API
        """
        logger.info(f"📊 {symbol} SEC 필링 수집 중...")

        try:
            # SEC EDGAR API
            url = f"https://data.sec.gov/submissions/CIK{self.get_cik(symbol)}.json"
            headers = {
                "User-Agent": "Aivesto aivesto@example.com"
            }

            # 임시 데이터 (실제 SEC API 응답 파싱 필요)
            filings = [
                {
                    "symbol": symbol,
                    "filing_type": "8-K",
                    "filing_date": "2025-11-15",
                    "description": "Results of Operations and Financial Condition",
                    "url": f"https://www.sec.gov/edgar/{symbol}/8-K"
                }
            ]

            logger.success(f"  ✅ {symbol} SEC 필링 {len(filings)}개 수집 완료")
            return filings

        except Exception as e:
            logger.error(f"  ❌ {symbol} SEC 필링 수집 실패: {e}")
            return []

    def get_cik(self, symbol: str) -> str:
        """종목 심볼에서 CIK 번호 가져오기"""
        # TODO: SEC CIK 매핑 테이블 구축
        cik_map = {
            "AAPL": "0000320193",
            "MSFT": "0000789019",
            "GOOGL": "0001652044",
            "AMZN": "0001018724",
            "NVDA": "0001045810"
        }
        return cik_map.get(symbol, "0000000000")

    def collect_insider_trading(self, symbol: str) -> List[Dict[str, Any]]:
        """
        내부자 매매 데이터 수집
        Source: FMP Insider Trading API
        """
        logger.info(f"📊 {symbol} 내부자 매매 수집 중...")

        if not self.fmp_key:
            logger.warning("FMP_API_KEY not set")
            return []

        try:
            url = f"https://financialmodelingprep.com/api/v4/insider-trading"
            params = {
                "symbol": symbol,
                "limit": 50,
                "apikey": self.fmp_key
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            insider_trades = []
            for trade in data[:10]:  # 최근 10건
                insider_trades.append({
                    "symbol": symbol,
                    "insider_name": trade.get("reportingName", ""),
                    "transaction_type": trade.get("transactionType", ""),
                    "shares": int(trade.get("securitiesTransacted", 0)),
                    "price": float(trade.get("price", 0)),
                    "filing_date": trade.get("filingDate", "")
                })

            logger.success(f"  ✅ {symbol} 내부자 매매 {len(insider_trades)}건 수집 완료")
            return insider_trades

        except Exception as e:
            logger.error(f"  ❌ {symbol} 내부자 매매 수집 실패: {e}")
            return []

    def collect_press_releases(self, symbol: str) -> List[Dict[str, Any]]:
        """
        기업 보도자료 수집
        Source: FMP Press Releases API
        """
        logger.info(f"📊 {symbol} 보도자료 수집 중...")

        if not self.fmp_key:
            logger.warning("FMP_API_KEY not set")
            return []

        try:
            url = f"https://financialmodelingprep.com/api/v3/press-releases/{symbol}"
            params = {
                "limit": 10,
                "apikey": self.fmp_key
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            press_releases = []
            for release in data:
                press_releases.append({
                    "symbol": symbol,
                    "title": release.get("title", ""),
                    "text": release.get("text", "")[:500],  # 500자만
                    "date": release.get("date", "")
                })

            logger.success(f"  ✅ {symbol} 보도자료 {len(press_releases)}개 수집 완료")
            return press_releases

        except Exception as e:
            logger.error(f"  ❌ {symbol} 보도자료 수집 실패: {e}")
            return []

    def analyze_event_signal(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        기업 이벤트에서 시그널 분석

        시그널 포인트:
        - 제품 리콜 → 즉각 하락
        - CEO 사임 → 단기 하락
        - M&A 발표 → 피인수 급등
        - 내부자 대량 매수 → 중기 상승
        """

        event_type = event.get("event_type", "")
        symbol = event.get("symbol")

        signal = {
            "symbol": symbol,
            "event_type": event_type,
            "signal": None,
            "severity": "MEDIUM"
        }

        # 이벤트별 시그널
        if "recall" in event_type.lower() or "리콜" in str(event.get("description", "")).lower():
            signal["signal"] = "IMMEDIATE_SELL"
            signal["severity"] = "CRITICAL"

        elif "ceo" in event_type.lower() and "resign" in event_type.lower():
            signal["signal"] = "SHORT_TERM_DOWN"
            signal["severity"] = "HIGH"

        elif "m&a" in event_type.lower() or "acquisition" in event_type.lower():
            signal["signal"] = "MA_ANNOUNCEMENT"
            signal["severity"] = "HIGH"

        elif event_type == "INSIDER_BUYING":
            # 내부자 매수량 확인
            shares = event.get("shares", 0)
            if shares > 100000:  # 10만 주 이상
                signal["signal"] = "INSIDER_STRONG_BUY"
                signal["severity"] = "HIGH"

        return signal

    def save_to_database(self, data: List[Dict[str, Any]]):
        """수집한 데이터를 Supabase에 저장"""

        logger.info("💾 Supabase에 저장 중...")

        for item in data:
            try:
                result = self.supabase.table('corporate_events').insert({
                    "symbol": item.get("symbol"),
                    "event_type": item.get("event_type"),
                    "event_description": item.get("description", ""),
                    "signal": item.get("signal", ""),
                    "severity": item.get("severity", "MEDIUM")
                }).execute()

                logger.success(f"  ✅ {item.get('symbol')} 저장 완료")

            except Exception as e:
                logger.error(f"  ❌ 저장 실패: {e}")

    def run(self):
        """기업 이벤트 수집 실행"""

        logger.info("=" * 60)
        logger.info("🚀 기업 이벤트 뉴스 수집 시작")
        logger.info("=" * 60)

        all_filings = []
        all_insider_trades = []
        all_press_releases = []

        # 각 종목별 데이터 수집
        for symbol in self.tracked_symbols[:3]:  # 테스트: 3개만
            # 1. SEC 필링
            filings = self.collect_sec_filings(symbol)
            all_filings.extend(filings)

            # 2. 내부자 매매
            insider_trades = self.collect_insider_trading(symbol)
            all_insider_trades.extend(insider_trades)

            # 3. 보도자료
            press_releases = self.collect_press_releases(symbol)
            all_press_releases.extend(press_releases)

        # 4. 시그널 분석
        signals = []
        for trade in all_insider_trades:
            if trade.get("transaction_type") == "P":  # Purchase
                event = {
                    "symbol": trade.get("symbol"),
                    "event_type": "INSIDER_BUYING",
                    "shares": trade.get("shares"),
                    "description": f"{trade.get('insider_name')} bought {trade.get('shares')} shares"
                }
                signal = self.analyze_event_signal(event)
                if signal.get("signal"):
                    signals.append(signal)

        # 5. 데이터베이스 저장
        if signals:
            self.save_to_database(signals)

        logger.info("\n" + "=" * 60)
        logger.success(f"✅ SEC 필링: {len(all_filings)}개")
        logger.success(f"✅ 내부자 매매: {len(all_insider_trades)}건")
        logger.success(f"✅ 보도자료: {len(all_press_releases)}개")
        logger.success(f"✅ 시그널 발견: {len(signals)}개")
        logger.info("=" * 60)

        return {
            "sec_filings": all_filings,
            "insider_trades": all_insider_trades,
            "press_releases": all_press_releases,
            "signals": signals
        }


def main():
    """메인 함수"""
    collector = CorporateEventsCollector()
    result = collector.run()


if __name__ == "__main__":
    main()
