"""
Reuters RSS 수집기 (Layer 1: Core Signal)
"""
from typing import List
from loguru import logger
import sys

sys.path.append('..')
from collectors.rss_fetcher import RSSFetcher
from collectors.base import BaseCollector
from database.models import RawNews


class ReutersCollector(BaseCollector):
    """Reuters 뉴스 수집기 (Layer 1)"""

    # Reuters 공개 RSS 피드
    FEEDS = [
        {
            'url': 'https://www.reuters.com/rssfeed/businessNews',
            'name': 'Reuters Business'
        },
        {
            'url': 'https://www.reuters.com/rssfeed/marketsNews',
            'name': 'Reuters Markets'
        },
        {
            'url': 'https://www.reuters.com/rssfeed/technologyNews',
            'name': 'Reuters Technology'
        }
    ]

    def __init__(self, db_client):
        super().__init__(db_client)
        self.fetchers = []

        for feed in self.FEEDS:
            fetcher = RSSFetcher(
                feed_url=feed['url'],
                source_name='Reuters',
                source_layer=1,  # Layer 1: Core Signal
                rate_limit=30  # Reuters: 30 req/min
            )
            self.fetchers.append(fetcher)

        logger.info(f"Reuters collector initialized with {len(self.fetchers)} feeds")

    def fetch_news(self) -> List[RawNews]:
        """Reuters 뉴스 수집"""
        all_articles = []

        for fetcher in self.fetchers:
            try:
                articles = fetcher.fetch_feed()

                for article in articles:
                    raw_news = RawNews(
                        source="Reuters (Layer 1)",
                        title=article['title'],
                        url=article['url'],
                        content=article['content'],
                        published_at=article['published_at'],
                        symbols=article['symbols'],
                        metadata={
                            'source_layer': 1,
                            'categories': article['categories'],
                            'feed_name': fetcher.source_name
                        }
                    )
                    all_articles.append(raw_news)

            except Exception as e:
                logger.error(f"Error in Reuters fetcher: {e}")

        logger.info(f"Reuters collected {len(all_articles)} articles")
        return all_articles
