import finnhub
from typing import List
from datetime import datetime, timedelta
from loguru import logger
import sys

sys.path.append('..')
from config.settings import FINNHUB_API_KEY, TRACKED_SYMBOLS
from database.models import RawNews
from collectors.base import BaseCollector

class FinnhubCollector(BaseCollector):
    """Finnhub API를 사용한 뉴스 수집기"""

    def __init__(self, db_client):
        super().__init__(db_client)
        self.client = finnhub.Client(api_key=FINNHUB_API_KEY)
        logger.info("Finnhub collector initialized")

    def fetch_news(self) -> List[RawNews]:
        """Finnhub에서 뉴스 수집"""
        news_items = []

        try:
            # 일반 시장 뉴스
            market_news = self._fetch_market_news()
            news_items.extend(market_news)

            # 종목별 뉴스 (주요 종목만 샘플링)
            for symbol in TRACKED_SYMBOLS[:5]:  # API 제한 고려
                company_news = self._fetch_company_news(symbol)
                news_items.extend(company_news)

        except Exception as e:
            logger.error(f"Finnhub fetch error: {e}")

        return news_items

    def _fetch_market_news(self) -> List[RawNews]:
        """시장 전체 뉴스"""
        news_items = []

        try:
            # 최근 24시간 뉴스
            today = datetime.now()
            yesterday = today - timedelta(days=1)

            news_data = self.client.general_news('general', minid=0)

            for item in news_data:
                try:
                    published_at = datetime.fromtimestamp(item['datetime'])

                    # 24시간 이내만
                    if published_at < yesterday:
                        continue

                    # 주식 심볼 추출
                    symbols = self.extract_symbols_from_text(
                        f"{item['headline']} {item['summary']}",
                        TRACKED_SYMBOLS
                    )

                    news = RawNews(
                        source="Finnhub",
                        title=item['headline'],
                        url=item['url'],
                        content=item['summary'],
                        published_at=published_at,
                        symbols=symbols,
                        metadata={
                            "category": item.get('category', ''),
                            "image": item.get('image', ''),
                            "related": item.get('related', '')
                        }
                    )
                    news_items.append(news)

                except Exception as e:
                    logger.error(f"Error parsing Finnhub news item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Finnhub market news fetch error: {e}")

        return news_items

    def _fetch_company_news(self, symbol: str) -> List[RawNews]:
        """특정 종목 뉴스"""
        news_items = []

        try:
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            news_data = self.client.company_news(symbol, _from=yesterday, to=today)

            for item in news_data:
                try:
                    published_at = datetime.fromtimestamp(item['datetime'])

                    news = RawNews(
                        source="Finnhub",
                        title=item['headline'],
                        url=item['url'],
                        content=item['summary'],
                        published_at=published_at,
                        symbols=[symbol],  # 명시적으로 심볼 포함
                        metadata={
                            "category": item.get('category', ''),
                            "image": item.get('image', ''),
                            "source": item.get('source', '')
                        }
                    )
                    news_items.append(news)

                except Exception as e:
                    logger.error(f"Error parsing company news for {symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Finnhub company news fetch error for {symbol}: {e}")

        return news_items
