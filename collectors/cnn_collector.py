"""
CNN Collector (Layer 2)
여론 증폭 감지용 - 진보 성향 뉴스
"""
from typing import List
import sys

sys.path.append('..')
from collectors.base import BaseCollector
from collectors.rss_fetcher import RSSFetcher
from database.models import RawNews
from loguru import logger


class CNNCollector(BaseCollector):
    """CNN RSS 수집기 (Layer 2 - Sentiment & Momentum)"""

    # CNN RSS 피드
    FEEDS = [
        {
            'url': 'http://rss.cnn.com/rss/cnn_topstories.rss',
            'name': 'CNN Top Stories'
        },
        {
            'url': 'http://rss.cnn.com/rss/money_news_economy.rss',
            'name': 'CNN Economy'
        },
        {
            'url': 'http://rss.cnn.com/rss/cnn_tech.rss',
            'name': 'CNN Tech'
        },
        {
            'url': 'http://rss.cnn.com/rss/cnn_allpolitics.rss',
            'name': 'CNN Politics'
        },
        {
            'url': 'http://rss.cnn.com/rss/cnn_us.rss',
            'name': 'CNN US'
        }
    ]

    def __init__(self, db_client):
        super().__init__(db_client)
        self.fetchers = []

        # 각 피드별로 RSSFetcher 생성
        for feed in self.FEEDS:
            fetcher = RSSFetcher(
                feed_url=feed['url'],
                source_name='CNN',
                source_layer=2,
                rate_limit=30
            )
            self.fetchers.append(fetcher)

        logger.info(f"CNN collector initialized with {len(self.fetchers)} feeds")

    def fetch_news(self) -> List[RawNews]:
        """CNN RSS 피드 수집"""
        all_articles = []

        for fetcher in self.fetchers:
            try:
                articles = fetcher.fetch_feed()

                # RawNews 객체로 변환
                for article in articles:
                    raw_news = RawNews(
                        source="CNN (Layer 2)",
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
                logger.error(f"Error in CNN fetcher: {e}")

        logger.info(f"CNN collected {len(all_articles)} articles")
        return all_articles
