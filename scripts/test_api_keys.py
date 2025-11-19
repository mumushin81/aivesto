#!/usr/bin/env python3
"""
API 키 검증 스크립트
모든 API 키가 올바르게 설정되었는지 확인합니다.
"""
import os
import sys
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def test_fred_api():
    """FRED API 키 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("1️⃣  FRED API 테스트")
    logger.info("=" * 60)

    api_key = os.getenv("FRED_API_KEY")

    if not api_key:
        logger.error("❌ FRED_API_KEY가 .env 파일에 설정되지 않았습니다")
        logger.info("   발급: https://fred.stlouisfed.org/")
        return False

    try:
        import requests

        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": "CPIAUCSL",
            "api_key": api_key,
            "file_type": "json",
            "limit": 1
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "observations" in data:
                logger.success("✅ FRED API 정상 작동")
                logger.info(f"   최근 CPI 데이터: {data['observations'][0]['value']}")
                return True
            else:
                logger.error(f"❌ FRED API 응답 형식 오류: {data}")
                return False
        elif response.status_code == 400:
            logger.error("❌ FRED API 키가 유효하지 않습니다")
            logger.info("   API 키를 다시 확인해주세요")
            return False
        else:
            logger.error(f"❌ FRED API 오류: HTTP {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ FRED API 테스트 실패: {e}")
        return False


def test_fmp_api():
    """FMP API 키 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  FMP API 테스트")
    logger.info("=" * 60)

    api_key = os.getenv("FMP_API_KEY")

    if not api_key:
        logger.error("❌ FMP_API_KEY가 .env 파일에 설정되지 않았습니다")
        logger.info("   발급: https://site.financialmodelingprep.com/")
        return False

    try:
        import requests

        url = f"https://financialmodelingprep.com/api/v3/quote/AAPL"
        params = {"apikey": api_key}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.success("✅ FMP API 정상 작동")
                logger.info(f"   AAPL 현재가: ${data[0]['price']}")
                return True
            else:
                logger.error(f"❌ FMP API 응답 형식 오류: {data}")
                return False
        elif response.status_code == 401:
            logger.error("❌ FMP API 키가 유효하지 않습니다")
            logger.info("   API 키를 다시 확인해주세요")
            return False
        elif response.status_code == 403:
            logger.error("❌ FMP API 일일 요청 한도 초과")
            logger.info("   무료 플랜: 250 requests/day")
            return False
        else:
            logger.error(f"❌ FMP API 오류: HTTP {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ FMP API 테스트 실패: {e}")
        return False


def test_alpha_vantage_api():
    """Alpha Vantage API 키 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  Alpha Vantage API 테스트")
    logger.info("=" * 60)

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        logger.error("❌ ALPHA_VANTAGE_API_KEY가 .env 파일에 설정되지 않았습니다")
        logger.info("   발급: https://www.alphavantage.co/support/#api-key")
        return False

    try:
        import requests

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "USD",
            "to_currency": "CNY",
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "Realtime Currency Exchange Rate" in data:
                rate = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
                logger.success("✅ Alpha Vantage API 정상 작동")
                logger.info(f"   USD/CNY 환율: {rate}")
                return True
            elif "Error Message" in data:
                logger.error(f"❌ Alpha Vantage API 오류: {data['Error Message']}")
                return False
            elif "Note" in data:
                logger.error("❌ Alpha Vantage API 요청 한도 초과")
                logger.info("   무료 플랜: 25 requests/day, 5 requests/minute")
                return False
            else:
                logger.error(f"❌ Alpha Vantage API 응답 형식 오류: {data}")
                return False
        else:
            logger.error(f"❌ Alpha Vantage API 오류: HTTP {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Alpha Vantage API 테스트 실패: {e}")
        return False


def test_yfinance():
    """yfinance 라이브러리 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("4️⃣  yfinance 테스트")
    logger.info("=" * 60)

    try:
        import yfinance as yf

        logger.info("   yfinance 패키지 설치됨")

        # NVDA 주가 조회
        nvda = yf.Ticker("NVDA")
        hist = nvda.history(period="1d")

        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            logger.success("✅ yfinance 정상 작동")
            logger.info(f"   NVDA 최근 종가: ${latest_price:.2f}")
            return True
        else:
            logger.error("❌ yfinance 데이터 조회 실패")
            return False

    except ImportError:
        logger.error("❌ yfinance 패키지가 설치되지 않았습니다")
        logger.info("   설치: pip install yfinance")
        return False
    except Exception as e:
        logger.error(f"❌ yfinance 테스트 실패: {e}")
        return False


def main():
    """모든 API 키 테스트 실행"""

    logger.info("=" * 60)
    logger.info("🔍 API 키 검증 시작")
    logger.info("=" * 60)

    results = {
        "FRED API": test_fred_api(),
        "FMP API": test_fmp_api(),
        "Alpha Vantage API": test_alpha_vantage_api(),
        "yfinance": test_yfinance()
    }

    # 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("📊 검증 결과 요약")
    logger.info("=" * 60)

    success_count = sum(results.values())
    total_count = len(results)

    for api_name, result in results.items():
        status = "✅ 정상" if result else "❌ 실패"
        logger.info(f"  {api_name}: {status}")

    logger.info("\n" + "=" * 60)
    logger.info(f"총 {success_count}/{total_count}개 API 정상 작동")
    logger.info("=" * 60)

    if success_count == total_count:
        logger.success("\n🎉 모든 API가 정상적으로 설정되었습니다!")
        logger.info("다음 단계: python scripts/news_collectors/tech_trends_collector.py")
        return 0
    else:
        logger.error("\n⚠️  일부 API 설정이 필요합니다.")
        logger.info("가이드: /docs/API_KEYS_SETUP_GUIDE.md")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
