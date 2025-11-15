"""
Wall Street Journal RSS 수집기 (Layer 1: Core Signal)
"""
from typing import List
from loguru import logger
import sys

sys.path.append('..')
from collectors.rss_fetcher import RSSFetcher
from collectors.base import BaseCollector
from database.models import RawNews


class WSJCollector(BaseCollector):
    """WSJ 뉴스 수집기 (Layer 1)"""

    # WSJ 공개 RSS 피드
    FEEDS = [
        {
            'url': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml',
            'name': 'WSJ US Business'
        },
        {
            'url': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
            'name': 'WSJ Markets'
        },
        {
            'url': 'https://feeds.a.dj.com/rss/RSSWSJD.xml',
            'name': 'WSJ Tech'
        }
    ]

    def __init__(self, db_client):
        super().__init__(db_client)
        self.fetchers = []

        for feed in self.FEEDS:
            fetcher = RSSFetcher(
                feed_url=feed['url'],
                source_name='WSJ',
                source_layer=1,  # Layer 1: Core Signal
                rate_limit=20  # WSJ: 20 req/min (보수적)
            )
            self.fetchers.append(fetcher)

        logger.info(f"WSJ collector initialized with {len(self.fetchers)} feeds")

    def fetch_news(self) -> List[RawNews]:
        """WSJ 뉴스 수집"""
        all_articles = []

        for fetcher in self.fetchers:
            try:
                articles = fetcher.fetch_feed()

                for article in articles:
                    raw_news = RawNews(
                        source="WSJ (Layer 1)",
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
                logger.error(f"Error in WSJ fetcher: {e}")

        logger.info(f"WSJ collected {len(all_articles)} articles")
        return all_articles
