from alpha_vantage.alphavantage import AlphaVantage
from typing import List
from datetime import datetime, timedelta
from loguru import logger
import requests
import sys

sys.path.append('..')
from config.settings import ALPHA_VANTAGE_API_KEY, TRACKED_SYMBOLS
from database.models import RawNews
from collectors.base import BaseCollector

class AlphaVantageCollector(BaseCollector):
    """Alpha Vantage API를 사용한 뉴스 수집기"""

    def __init__(self, db_client):
        super().__init__(db_client)
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        logger.info("Alpha Vantage collector initialized")

    def fetch_news(self) -> List[RawNews]:
        """Alpha Vantage에서 뉴스 수집"""
        news_items = []

        try:
            # 시장 뉴스 & 감성 분석
            market_news = self._fetch_news_sentiment()
            news_items.extend(market_news)

            # 종목별 뉴스
            for symbol in TRACKED_SYMBOLS[:3]:  # API 제한 고려 (무료: 25 req/day)
                symbol_news = self._fetch_news_sentiment(symbol)
                news_items.extend(symbol_news)

        except Exception as e:
            logger.error(f"Alpha Vantage fetch error: {e}")

        return news_items

    def _fetch_news_sentiment(self, ticker: str = None) -> List[RawNews]:
        """뉴스 & 감성 분석 데이터 수집"""
        news_items = []

        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "apikey": self.api_key,
                "limit": 50
            }

            if ticker:
                params["tickers"] = ticker

            response = requests.get(self.base_url, params=params)
            data = response.json()

            if "feed" not in data:
                logger.warning(f"No news feed in Alpha Vantage response: {data}")
                return news_items

            yesterday = datetime.now() - timedelta(days=1)

            for item in data["feed"]:
                try:
                    # 시간 파싱 (ISO 8601 형식)
                    published_str = item['time_published']
                    published_at = datetime.strptime(published_str, '%Y%m%dT%H%M%S')

                    # 24시간 이내만
                    if published_at < yesterday:
                        continue

                    # 종목 심볼 추출
                    symbols = []
                    if "ticker_sentiment" in item:
                        symbols = [t["ticker"] for t in item["ticker_sentiment"]]

                    # 추가 심볼 추출
                    extracted_symbols = self.extract_symbols_from_text(
                        f"{item['title']} {item.get('summary', '')}",
                        TRACKED_SYMBOLS
                    )
                    symbols.extend(extracted_symbols)
                    symbols = list(set(symbols))  # 중복 제거

                    # 감성 분석 메타데이터
                    sentiment_score = float(item.get('overall_sentiment_score', 0))
                    sentiment_label = item.get('overall_sentiment_label', 'Neutral')

                    news = RawNews(
                        source="Alpha Vantage",
                        title=item['title'],
                        url=item['url'],
                        content=item.get('summary', ''),
                        published_at=published_at,
                        symbols=symbols,
                        metadata={
                            "sentiment_score": sentiment_score,
                            "sentiment_label": sentiment_label,
                            "topics": item.get('topics', []),
                            "authors": item.get('authors', []),
                            "source": item.get('source', '')
                        }
                    )
                    news_items.append(news)

                except Exception as e:
                    logger.error(f"Error parsing Alpha Vantage news item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Alpha Vantage API request error: {e}")

        return news_items
