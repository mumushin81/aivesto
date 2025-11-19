#!/usr/bin/env python3
"""
국제 뉴스 & 지정학적 리스크 수집기

수집 대상:
- 중국 경제 지표
- 홍콩·상해 지수 급등락
- 러시아-우크라이나 전쟁
- 중동 분쟁
- 국제유가 급등락
- 환율 변동 (DXY, USD/CNY)

데이터 소스:
- Reuters World
- Bloomberg Asia
- CNBC International
- Trading Economics
- OANDA (환율)
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from typing import List, Dict, Any
import yfinance as yf

load_dotenv()


class GeopoliticalCollector:
    """지정학적 뉴스 수집기"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")

        # 지역별 영향 받는 섹터/종목
        self.geopolitical_impact = {
            "CHINA": {
                "affected_stocks": ["AAPL", "TSLA", "NVDA", "AMD"],
                "sectors": ["TECH", "AUTOMOTIVE", "SEMICONDUCTOR"]
            },
            "MIDDLE_EAST": {
                "affected_stocks": ["XOM", "CVX", "OXY"],
                "sectors": ["ENERGY", "OIL"]
            },
            "RUSSIA": {
                "affected_stocks": ["LMT", "RTX", "GD"],
                "sectors": ["DEFENSE", "AEROSPACE"]
            }
        }

    def collect_china_indicators(self) -> List[Dict[str, Any]]:
        """
        중국 경제 지표 수집
        Source: Trading Economics API or Alpha Vantage
        """
        logger.info("📊 중국 경제 지표 수집 중...")

        try:
            # 중국 주요 지수
            china_indices = {
                "000001.SS": "Shanghai Composite",
                "HSI": "Hang Seng Index"
            }

            china_data = []

            for symbol, name in china_indices.items():
                index = yf.Ticker(symbol)
                hist = index.history(period="5d")

                if not hist.empty:
                    latest_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((latest_close - prev_close) / prev_close) * 100

                    china_data.append({
                        "index": name,
                        "symbol": symbol,
                        "price": float(latest_close),
                        "change_pct": float(change_pct),
                        "date": datetime.now().date().isoformat()
                    })

                    logger.success(f"  ✅ {name}: {change_pct:.2f}%")

            return china_data

        except Exception as e:
            logger.error(f"  ❌ 중국 지표 수집 실패: {e}")
            return []

    def collect_currency_data(self) -> List[Dict[str, Any]]:
        """
        환율 데이터 수집 (DXY, USD/CNY)
        Source: Alpha Vantage FX
        """
        logger.info("📊 환율 데이터 수집 중...")

        try:
            currency_pairs = {
                "DX-Y.NYB": "Dollar Index (DXY)",
                "CNY=X": "USD/CNY"
            }

            currency_data = []

            for symbol, name in currency_pairs.items():
                fx = yf.Ticker(symbol)
                hist = fx.history(period="5d")

                if not hist.empty:
                    latest_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((latest_close - prev_close) / prev_close) * 100

                    currency_data.append({
                        "pair": name,
                        "symbol": symbol,
                        "rate": float(latest_close),
                        "change_pct": float(change_pct),
                        "date": datetime.now().date().isoformat()
                    })

                    logger.success(f"  ✅ {name}: {latest_close:.2f} ({change_pct:+.2f}%)")

            return currency_data

        except Exception as e:
            logger.error(f"  ❌ 환율 데이터 수집 실패: {e}")
            return []

    def collect_oil_prices(self) -> List[Dict[str, Any]]:
        """
        국제 유가 수집
        Source: yfinance (WTI, Brent)
        """
        logger.info("📊 국제 유가 수집 중...")

        try:
            oil_symbols = {
                "CL=F": "WTI Crude Oil",
                "BZ=F": "Brent Crude Oil"
            }

            oil_data = []

            for symbol, name in oil_symbols.items():
                oil = yf.Ticker(symbol)
                hist = oil.history(period="5d")

                if not hist.empty:
                    latest_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((latest_close - prev_close) / prev_close) * 100

                    oil_data.append({
                        "commodity": name,
                        "symbol": symbol,
                        "price": float(latest_close),
                        "change_pct": float(change_pct),
                        "date": datetime.now().date().isoformat()
                    })

                    logger.success(f"  ✅ {name}: ${latest_close:.2f} ({change_pct:+.2f}%)")

            return oil_data

        except Exception as e:
            logger.error(f"  ❌ 유가 데이터 수집 실패: {e}")
            return []

    def analyze_geopolitical_signal(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        지정학적 데이터에서 시그널 분석

        시그널 포인트:
        - 중국 경기침체 → AAPL, TSLA 하락
        - 전쟁 확대 → 방산 상승
        - 달러 강세 → 성장주 하락
        """

        signal = {
            "region": None,
            "event_type": data_type,
            "signal": None,
            "affected_stocks": [],
            "impact_level": "MEDIUM"
        }

        if data_type == "CHINA_INDEX":
            change_pct = data.get("change_pct", 0)

            if change_pct < -3:  # 중국 지수 3% 이상 하락
                signal["region"] = "CHINA"
                signal["signal"] = "CHINA_MARKET_DOWN"
                signal["affected_stocks"] = self.geopolitical_impact["CHINA"]["affected_stocks"]
                signal["impact_level"] = "HIGH"

        elif data_type == "CURRENCY":
            pair = data.get("pair", "")
            rate = data.get("rate", 0)
            change_pct = data.get("change_pct", 0)

            if "DXY" in pair and rate > 105:  # 달러 지수 105 이상
                signal["region"] = "GLOBAL"
                signal["signal"] = "DOLLAR_STRONG_GROWTH_DOWN"
                signal["affected_stocks"] = ["QQQ", "ARKK"]
                signal["impact_level"] = "HIGH"

        elif data_type == "OIL":
            change_pct = data.get("change_pct", 0)

            if change_pct > 5:  # 유가 5% 이상 급등
                signal["region"] = "MIDDLE_EAST"
                signal["signal"] = "OIL_SURGE_ENERGY_UP"
                signal["affected_stocks"] = self.geopolitical_impact["MIDDLE_EAST"]["affected_stocks"]
                signal["impact_level"] = "HIGH"

        return signal

    def save_to_database(self, data: List[Dict[str, Any]]):
        """수집한 데이터를 Supabase에 저장"""

        logger.info("💾 Supabase에 저장 중...")

        for item in data:
            try:
                result = self.supabase.table('geopolitical_news').insert({
                    "region": item.get("region", "UNKNOWN"),
                    "event_type": item.get("event_type", ""),
                    "affected_sectors": item.get("affected_stocks", []),
                    "signal": item.get("signal", "")
                }).execute()

                logger.success(f"  ✅ {item.get('region')} 저장 완료")

            except Exception as e:
                logger.error(f"  ❌ 저장 실패: {e}")

    def run(self):
        """지정학적 뉴스 수집 실행"""

        logger.info("=" * 60)
        logger.info("🚀 지정학적 뉴스 수집 시작")
        logger.info("=" * 60)

        # 1. 중국 경제 지표
        china_data = self.collect_china_indicators()

        # 2. 환율 데이터
        currency_data = self.collect_currency_data()

        # 3. 국제 유가
        oil_data = self.collect_oil_prices()

        # 4. 시그널 분석
        signals = []

        for data in china_data:
            signal = self.analyze_geopolitical_signal(data, "CHINA_INDEX")
            if signal.get("signal"):
                signals.append(signal)

        for data in currency_data:
            signal = self.analyze_geopolitical_signal(data, "CURRENCY")
            if signal.get("signal"):
                signals.append(signal)

        for data in oil_data:
            signal = self.analyze_geopolitical_signal(data, "OIL")
            if signal.get("signal"):
                signals.append(signal)

        # 5. 데이터베이스 저장
        if signals:
            self.save_to_database(signals)

        logger.info("\n" + "=" * 60)
        logger.success(f"✅ 중국 지표: {len(china_data)}개")
        logger.success(f"✅ 환율 데이터: {len(currency_data)}개")
        logger.success(f"✅ 유가 데이터: {len(oil_data)}개")
        logger.success(f"✅ 시그널 발견: {len(signals)}개")
        logger.info("=" * 60)

        return {
            "china": china_data,
            "currency": currency_data,
            "oil": oil_data,
            "signals": signals
        }


def main():
    """메인 함수"""
    collector = GeopoliticalCollector()
    result = collector.run()


if __name__ == "__main__":
    main()
