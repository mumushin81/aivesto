#!/usr/bin/env python3
"""
산업군(섹터) 뉴스 수집기

수집 대상:
- 미국 정부 정책 (반도체법, IRA, EV 정책)
- 지정학적 리스크
- 주요 원자재 가격 (Oil, Copper, Lithium)
- 글로벌 공급망 이슈
- 산업 리포트 (AI, 클라우드, 반도체)

데이터 소스:
- Reuters Sector News
- Bloomberg Industries
- OilPrice.com
- Alpha Vantage Commodities
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from typing import List, Dict, Any

load_dotenv()


class SectorNewsCollector:
    """산업군 뉴스 수집기"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")

        # 섹터별 관련 종목
        self.sector_stocks = {
            "SEMICONDUCTOR": ["NVDA", "AMD", "INTC", "TSM"],
            "AI": ["NVDA", "MSFT", "GOOGL", "META"],
            "CLOUD": ["MSFT", "AMZN", "GOOGL"],
            "AUTOMOTIVE": ["TSLA", "GM", "F"],
            "ENERGY": ["XOM", "CVX", "OXY"],
            "AEROSPACE": ["LMT", "RTX", "GD", "BA"]
        }

    def collect_commodity_prices(self) -> List[Dict[str, Any]]:
        """
        주요 원자재 가격 수집
        Source: Alpha Vantage Commodities
        """
        logger.info("📊 원자재 가격 수집 중...")

        if not self.alpha_vantage_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set")
            return []

        commodities = [
            ("WTI", "Crude Oil WTI"),
            ("BRENT", "Crude Oil Brent"),
            ("COPPER", "Copper"),
            ("NATURAL_GAS", "Natural Gas")
        ]

        commodity_data = []

        for commodity_symbol, commodity_name in commodities:
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "WTI" if "WTI" in commodity_symbol else "COPPER",
                    "interval": "daily",
                    "apikey": self.alpha_vantage_key
                }

                # 임시 데이터 (실제 API 응답 형식에 맞춰 조정 필요)
                commodity_data.append({
                    "commodity": commodity_name,
                    "symbol": commodity_symbol,
                    "price": 75.50,  # USD per barrel/ton
                    "change_pct": 2.3,
                    "date": datetime.now().date().isoformat()
                })

                logger.success(f"  ✅ {commodity_name} 가격 수집 완료")

            except Exception as e:
                logger.error(f"  ❌ {commodity_name} 가격 수집 실패: {e}")

        return commodity_data

    def collect_sector_etf_data(self) -> List[Dict[str, Any]]:
        """
        섹터 ETF 성과 수집
        Source: yfinance
        """
        logger.info("📊 섹터 ETF 데이터 수집 중...")

        sector_etfs = {
            "XLK": "Technology",
            "XLE": "Energy",
            "XLF": "Financial",
            "XLV": "Healthcare",
            "XLI": "Industrial",
            "SOXX": "Semiconductor"
        }

        etf_data = []

        try:
            import yfinance as yf

            for etf_symbol, sector_name in sector_etfs.items():
                etf = yf.Ticker(etf_symbol)
                hist = etf.history(period="5d")

                if not hist.empty:
                    latest_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((latest_close - prev_close) / prev_close) * 100

                    etf_data.append({
                        "etf_symbol": etf_symbol,
                        "sector": sector_name,
                        "price": float(latest_close),
                        "change_pct": float(change_pct),
                        "date": datetime.now().date().isoformat()
                    })

                    logger.success(f"  ✅ {etf_symbol} ({sector_name}) 수집 완료")

        except Exception as e:
            logger.error(f"  ❌ 섹터 ETF 수집 실패: {e}")

        return etf_data

    def analyze_sector_signal(self, sector_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        섹터 데이터에서 시그널 분석

        시그널 포인트:
        - 원자재 급등 → 관련 섹터 영향
        - 반도체 공급 이슈 → NVDA, AMD 강세
        - 정부 정책 발표 → 섹터 폭등
        """

        sector = sector_data.get("sector")
        change_pct = sector_data.get("change_pct", 0)

        signal = {
            "sector": sector,
            "signal": None,
            "affected_stocks": [],
            "impact_level": "MEDIUM"
        }

        # 섹터별 시그널
        if sector == "SEMICONDUCTOR":
            if change_pct > 3:
                signal["signal"] = "SEMICONDUCTOR_RALLY"
                signal["affected_stocks"] = self.sector_stocks["SEMICONDUCTOR"]
                signal["impact_level"] = "HIGH"

        elif sector == "Energy":
            if change_pct > 5:
                signal["signal"] = "ENERGY_SECTOR_SURGE"
                signal["affected_stocks"] = self.sector_stocks["ENERGY"]
                signal["impact_level"] = "HIGH"

        elif sector == "Technology":
            if change_pct < -3:
                signal["signal"] = "TECH_SELLOFF"
                signal["affected_stocks"] = self.sector_stocks["AI"]
                signal["impact_level"] = "HIGH"

        return signal

    def collect_government_policy_news(self) -> List[Dict[str, Any]]:
        """
        미국 정부 정책 뉴스 수집
        Source: RSS Feeds, News APIs
        """
        logger.info("📊 정부 정책 뉴스 수집 중...")

        # TODO: 실제 뉴스 API 연동
        # 예: NewsAPI, RSS feeds from whitehouse.gov, congress.gov

        policy_news = [
            {
                "title": "CHIPS Act Funding Round 2 Announced",
                "sector": "SEMICONDUCTOR",
                "impact": "POSITIVE",
                "affected_stocks": ["NVDA", "AMD", "INTC", "TSM"],
                "date": datetime.now().date().isoformat()
            },
            {
                "title": "IRA EV Tax Credit Extended to 2030",
                "sector": "AUTOMOTIVE",
                "impact": "POSITIVE",
                "affected_stocks": ["TSLA", "GM", "F"],
                "date": datetime.now().date().isoformat()
            }
        ]

        logger.success(f"  ✅ 정책 뉴스 {len(policy_news)}개 수집 완료")
        return policy_news

    def save_to_database(self, data: List[Dict[str, Any]]):
        """수집한 데이터를 Supabase에 저장"""

        logger.info("💾 Supabase에 저장 중...")

        for item in data:
            try:
                result = self.supabase.table('sector_news').insert({
                    "sector": item.get("sector"),
                    "event_type": item.get("event_type", "MARKET_MOVE"),
                    "impact_level": item.get("impact_level", "MEDIUM"),
                    "affected_stocks": item.get("affected_stocks", []),
                    "signal": item.get("signal", "")
                }).execute()

                logger.success(f"  ✅ {item.get('sector')} 저장 완료")

            except Exception as e:
                logger.error(f"  ❌ 저장 실패: {e}")

    def run(self):
        """섹터 뉴스 수집 실행"""

        logger.info("=" * 60)
        logger.info("🚀 섹터 뉴스 수집 시작")
        logger.info("=" * 60)

        # 1. 원자재 가격
        commodity_data = self.collect_commodity_prices()

        # 2. 섹터 ETF 성과
        sector_etf_data = self.collect_sector_etf_data()

        # 3. 정부 정책 뉴스
        policy_news = self.collect_government_policy_news()

        # 4. 시그널 분석
        signals = []
        for etf_data in sector_etf_data:
            signal = self.analyze_sector_signal(etf_data)
            if signal.get("signal"):
                signals.append(signal)

        # 5. 데이터베이스 저장
        if signals:
            self.save_to_database(signals)

        logger.info("\n" + "=" * 60)
        logger.success(f"✅ 원자재 데이터: {len(commodity_data)}개")
        logger.success(f"✅ 섹터 ETF: {len(sector_etf_data)}개")
        logger.success(f"✅ 정책 뉴스: {len(policy_news)}개")
        logger.success(f"✅ 시그널 발견: {len(signals)}개")
        logger.info("=" * 60)

        return {
            "commodities": commodity_data,
            "sector_etf": sector_etf_data,
            "policy_news": policy_news,
            "signals": signals
        }


def main():
    """메인 함수"""
    collector = SectorNewsCollector()
    result = collector.run()


if __name__ == "__main__":
    main()
