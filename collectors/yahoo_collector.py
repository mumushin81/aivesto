"""
Yahoo Finance Collector (Layer 2)
여론 증폭 감지용 - 금융 뉴스 대중화
"""
from typing import List
import sys

sys.path.append('..')
from collectors.base import BaseCollector
from collectors.rss_fetcher import RSSFetcher
from database.models import RawNews
from loguru import logger


class YahooCollector(BaseCollector):
    """Yahoo Finance RSS 수집기 (Layer 2 - Sentiment & Momentum)"""

    # Yahoo Finance RSS 피드
    FEEDS = [
        {
            'url': 'https://finance.yahoo.com/news/rssindex',
            'name': 'Yahoo Finance News'
        },
        {
            'url': 'https://finance.yahoo.com/rss/topstories',
            'name': 'Yahoo Finance Top Stories'
        }
    ]

    def __init__(self, db_client):
        super().__init__(db_client)
        self.fetchers = []

        # 각 피드별로 RSSFetcher 생성
        for feed in self.FEEDS:
            fetcher = RSSFetcher(
                feed_url=feed['url'],
                source_name='Yahoo Finance',
                source_layer=2,
                rate_limit=30
            )
            self.fetchers.append(fetcher)

        logger.info(f"Yahoo Finance collector initialized with {len(self.fetchers)} feeds")

    def fetch_news(self) -> List[RawNews]:
        """Yahoo Finance RSS 피드 수집"""
        all_articles = []

        for fetcher in self.fetchers:
            try:
                articles = fetcher.fetch_feed()

                # RawNews 객체로 변환
                for article in articles:
                    raw_news = RawNews(
                        source="Yahoo Finance (Layer 2)",
                        title=article['title'],
                        url=article['url'],
                        content=article['content'],
                        published_at=article['published_at'],
                        symbols=article['symbols'],
                        metadata={
                            'source_layer': 2,
                            'categories': article['categories'],
                            'feed_name': fetcher.source_name
                        }
                    )
                    all_articles.append(raw_news)

            except Exception as e:
                logger.error(f"Error in Yahoo Finance fetcher: {e}")

        logger.info(f"Yahoo Finance collected {len(all_articles)} articles")
        return all_articles
