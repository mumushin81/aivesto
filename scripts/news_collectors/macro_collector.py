#!/usr/bin/env python3
"""
거시경제(Macro) 뉴스 수집기

수집 대상:
- CPI, PPI (소비자/생산자 물가지수)
- 고용지표: NFP, 실업률
- FOMC: 의사록, 금리 결정
- 소매판매, 제조업 PMI
- GDP 성장률
- 소비자신뢰지수
- 미 재무부/연준 발언

데이터 소스:
- CNBC Economy API
- Bloomberg Markets
- Investing.com Economic Calendar
- Reuters Economics
- 미국 정부 공식 리포트 (BEA, BLS)
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from typing import List, Dict, Any

load_dotenv()


class MacroNewsCollector:
    """거시경제 뉴스 수집기"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        # API Keys (환경변수로 설정)
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.fred_key = os.getenv("FRED_API_KEY")  # Federal Reserve Economic Data

    def collect_cpi_data(self) -> List[Dict[str, Any]]:
        """
        CPI (Consumer Price Index) 데이터 수집
        Source: FRED API
        """
        logger.info("📊 CPI 데이터 수집 중...")

        if not self.fred_key:
            logger.warning("FRED_API_KEY not set")
            return []

        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "CPIAUCSL",  # CPI for All Urban Consumers
                "api_key": self.fred_key,
                "file_type": "json",
                "limit": 12,  # 최근 12개월
                "sort_order": "desc"
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            observations = data.get("observations", [])

            cpi_data = []
            for obs in observations:
                cpi_data.append({
                    "date": obs.get("date"),
                    "value": float(obs.get("value", 0)),
                    "indicator": "CPI"
                })

            logger.success(f"  ✅ CPI 데이터 {len(cpi_data)}개 수집 완료")
            return cpi_data

        except Exception as e:
            logger.error(f"  ❌ CPI 데이터 수집 실패: {e}")
            return []

    def collect_unemployment_data(self) -> List[Dict[str, Any]]:
        """
        실업률 데이터 수집
        Source: FRED API
        """
        logger.info("📊 실업률 데이터 수집 중...")

        if not self.fred_key:
            logger.warning("FRED_API_KEY not set")
            return []

        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "UNRATE",  # Unemployment Rate
                "api_key": self.fred_key,
                "file_type": "json",
                "limit": 12,
                "sort_order": "desc"
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            observations = data.get("observations", [])

            unemployment_data = []
            for obs in observations:
                unemployment_data.append({
                    "date": obs.get("date"),
                    "value": float(obs.get("value", 0)),
                    "indicator": "UNEMPLOYMENT_RATE"
                })

            logger.success(f"  ✅ 실업률 데이터 {len(unemployment_data)}개 수집 완료")
            return unemployment_data

        except Exception as e:
            logger.error(f"  ❌ 실업률 데이터 수집 실패: {e}")
            return []

    def collect_gdp_data(self) -> List[Dict[str, Any]]:
        """
        GDP 성장률 데이터 수집
        Source: FRED API
        """
        logger.info("📊 GDP 데이터 수집 중...")

        if not self.fred_key:
            logger.warning("FRED_API_KEY not set")
            return []

        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "GDP",  # Gross Domestic Product
                "api_key": self.fred_key,
                "file_type": "json",
                "limit": 8,  # 최근 8분기 (2년)
                "sort_order": "desc"
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            observations = data.get("observations", [])

            gdp_data = []
            for obs in observations:
                gdp_data.append({
                    "date": obs.get("date"),
                    "value": float(obs.get("value", 0)),
                    "indicator": "GDP"
                })

            logger.success(f"  ✅ GDP 데이터 {len(gdp_data)}개 수집 완료")
            return gdp_data

        except Exception as e:
            logger.error(f"  ❌ GDP 데이터 수집 실패: {e}")
            return []

    def collect_fomc_calendar(self) -> List[Dict[str, Any]]:
        """
        FOMC 회의 일정 수집
        Source: Federal Reserve 공식 웹사이트 (스크래핑)
        """
        logger.info("📊 FOMC 일정 수집 중...")

        # TODO: Federal Reserve 웹사이트 스크래핑
        # https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

        # 임시 데이터 (실제 구현 시 스크래핑 필요)
        fomc_data = [
            {
                "date": "2025-01-29",
                "event": "FOMC Meeting",
                "description": "Federal Open Market Committee Meeting"
            },
            {
                "date": "2025-03-19",
                "event": "FOMC Meeting",
                "description": "Federal Open Market Committee Meeting"
            }
        ]

        logger.success(f"  ✅ FOMC 일정 {len(fomc_data)}개 수집 완료")
        return fomc_data

    def analyze_macro_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        거시경제 데이터에서 시그널 분석

        시그널 포인트:
        - CPI > 예상 → Tech/성장주 하락
        - 실업률 < 예상 → 달러 강세 → 나스닥 하락
        - GDP 강세 → 금리 상승 기대
        """

        indicator = data.get("indicator")
        value = data.get("value", 0)

        signal = {
            "indicator": indicator,
            "value": value,
            "date": data.get("date"),
            "signal": None,
            "affected_sectors": [],
            "impact_level": "MEDIUM"
        }

        # CPI 시그널
        if indicator == "CPI":
            # 전월 대비 증가율 계산 (실제로는 consensus와 비교)
            if value > 3.0:  # 임계값 (실제로는 동적으로 계산)
                signal["signal"] = "TECH_GROWTH_SHORT_TERM_DOWN"
                signal["affected_sectors"] = ["TECH", "GROWTH_STOCKS"]
                signal["impact_level"] = "HIGH"
            elif value < 2.0:
                signal["signal"] = "RISK_ON_RALLY"
                signal["affected_sectors"] = ["TECH", "GROWTH_STOCKS"]
                signal["impact_level"] = "HIGH"

        # 실업률 시그널
        elif indicator == "UNEMPLOYMENT_RATE":
            if value < 4.0:  # 낮은 실업률 → 경기 과열 우려
                signal["signal"] = "DOLLAR_STRONG_NASDAQ_DOWN"
                signal["affected_sectors"] = ["NASDAQ", "QQQ"]
                signal["impact_level"] = "HIGH"
            elif value > 5.0:  # 높은 실업률 → 경기 둔화
                signal["signal"] = "RECESSION_RISK"
                signal["affected_sectors"] = ["ALL"]
                signal["impact_level"] = "CRITICAL"

        # GDP 시그널
        elif indicator == "GDP":
            # 전분기 대비 증가율 (실제로는 계산 필요)
            if value > 20000:  # 임시 기준 (실제로는 YoY 성장률)
                signal["signal"] = "ECONOMY_STRONG_RATE_HIKE_RISK"
                signal["affected_sectors"] = ["BONDS", "TECH"]
                signal["impact_level"] = "HIGH"

        return signal

    def save_to_database(self, data: List[Dict[str, Any]]):
        """수집한 데이터를 Supabase에 저장"""

        logger.info("💾 Supabase에 저장 중...")

        for item in data:
            try:
                # macro_news 테이블에 저장
                result = self.supabase.table('macro_news').insert({
                    "event_type": item.get("indicator"),
                    "actual": item.get("value"),
                    "consensus": None,  # TODO: consensus 데이터 추가
                    "previous": None,  # TODO: previous 데이터 추가
                    "impact": "HIGH",
                    "affected_sectors": item.get("affected_sectors", []),
                }).execute()

                logger.success(f"  ✅ {item.get('indicator')} 저장 완료")

            except Exception as e:
                logger.error(f"  ❌ 저장 실패: {e}")

    def run(self):
        """거시경제 뉴스 수집 실행"""

        logger.info("=" * 60)
        logger.info("🚀 거시경제 뉴스 수집 시작")
        logger.info("=" * 60)

        all_data = []

        # 1. CPI 데이터
        cpi_data = self.collect_cpi_data()
        all_data.extend(cpi_data)

        # 2. 실업률 데이터
        unemployment_data = self.collect_unemployment_data()
        all_data.extend(unemployment_data)

        # 3. GDP 데이터
        gdp_data = self.collect_gdp_data()
        all_data.extend(gdp_data)

        # 4. FOMC 일정
        fomc_data = self.collect_fomc_calendar()

        # 5. 시그널 분석
        logger.info("\n📊 시그널 분석 중...")
        signals = []
        for data_point in all_data:
            signal = self.analyze_macro_signal(data_point)
            if signal.get("signal"):
                signals.append(signal)
                logger.info(f"  📈 {signal['indicator']}: {signal['signal']}")

        # 6. 데이터베이스 저장
        if all_data:
            self.save_to_database(all_data)

        logger.info("\n" + "=" * 60)
        logger.success(f"✅ 거시경제 데이터 수집 완료: {len(all_data)}개")
        logger.success(f"✅ 시그널 발견: {len(signals)}개")
        logger.info("=" * 60)

        return {
            "data": all_data,
            "signals": signals,
            "fomc_calendar": fomc_data
        }


def main():
    """메인 함수"""
    collector = MacroNewsCollector()
    result = collector.run()

    # 결과 출력
    if result["signals"]:
        logger.info("\n🎯 발견된 시그널:")
        for signal in result["signals"]:
            logger.info(f"  - {signal['indicator']}: {signal['signal']}")
            logger.info(f"    영향 섹터: {', '.join(signal['affected_sectors'])}")
            logger.info(f"    영향도: {signal['impact_level']}\n")


if __name__ == "__main__":
    main()
