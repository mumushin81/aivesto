"""
Bloomberg RSS 수집기 (Layer 1: Core Signal)
"""
from typing import List
from loguru import logger
import sys

sys.path.append('..')
from collectors.rss_fetcher import RSSFetcher
from collectors.base import BaseCollector
from database.models import RawNews


class BloombergCollector(BaseCollector):
    """Bloomberg 뉴스 수집기 (Layer 1)"""

    # Bloomberg 공개 RSS 피드
    FEEDS = [
        {
            'url': 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
            'name': 'Bloomberg ETF Report'
        },
        {
            'url': 'https://www.bloomberg.com/politics/feeds/site.xml',
            'name': 'Bloomberg Politics'
        },
        # 추가 피드는 발견 시 업데이트
    ]

    def __init__(self, db_client):
        super().__init__(db_client)
        self.fetchers = []

        # 각 피드별로 RSSFetcher 생성
        for feed in self.FEEDS:
            fetcher = RSSFetcher(
                feed_url=feed['url'],
                source_name='Bloomberg',
                source_layer=1,  # Layer 1: Core Signal
                rate_limit=20  # Bloomberg: 20 req/min
            )
            self.fetchers.append(fetcher)

        logger.info(f"Bloomberg collector initialized with {len(self.fetchers)} feeds")

    def fetch_news(self) -> List[RawNews]:
        """Bloomberg 뉴스 수집"""
        all_articles = []

        for fetcher in self.fetchers:
            try:
                articles = fetcher.fetch_feed()

                # RawNews 객체로 변환
                for article in articles:
                    raw_news = RawNews(
                        source="Bloomberg (Layer 1)",
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
                logger.error(f"Error in Bloomberg fetcher: {e}")

        logger.info(f"Bloomberg collected {len(all_articles)} articles")
        return all_articles
