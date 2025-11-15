"""
공통 RSS 피드 수집 유틸리티
Multi-layer news collection support
"""
import feedparser
import hashlib
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import httpx
from bs4 import BeautifulSoup


class RSSFetcher:
    """RSS 피드 수집 및 파싱 유틸리티"""

    def __init__(self, feed_url: str, source_name: str, source_layer: int, rate_limit: int = 30):
        """
        Args:
            feed_url: RSS 피드 URL
            source_name: 소스 이름 (예: "Bloomberg", "Reuters")
            source_layer: 1 (Core), 2 (Sentiment), 3 (Broad)
            rate_limit: 분당 최대 요청 수
        """
        self.feed_url = feed_url
        self.source_name = source_name
        self.source_layer = source_layer
        self.rate_limit = rate_limit
        self.seen_urls = set()  # 중복 방지
        self.semaphore = asyncio.Semaphore(rate_limit)

        logger.info(f"RSSFetcher initialized: {source_name} (Layer {source_layer})")

    def fetch_feed(self) -> List[Dict]:
        """
        RSS 피드 동기 수집

        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Fetching RSS feed: {self.feed_url}")
            feed = feedparser.parse(self.feed_url)

            if feed.bozo:
                logger.warning(f"Malformed RSS feed: {self.feed_url}")

            articles = []
            for entry in feed.entries:
                article = self._parse_entry(entry)
                if article and article['url'] not in self.seen_urls:
                    self.seen_urls.add(article['url'])
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} new articles from {self.source_name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed {self.feed_url}: {e}")
            return []

    def _parse_entry(self, entry) -> Optional[Dict]:
        """
        RSS 엔트리 파싱

        Args:
            entry: feedparser entry object

        Returns:
            Article dictionary or None
        """
        try:
            # 기본 정보 추출
            title = entry.get('title', 'No title')
            url = entry.get('link', '')

            # 내용 추출 (summary 또는 content)
            content = ''
            if 'summary' in entry:
                content = entry.summary
            elif 'content' in entry:
                content = entry.content[0].get('value', '')

            # HTML 태그 제거
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text().strip()

            # 발행 시각
            published_at = self._parse_datetime(entry)

            # 카테고리
            categories = [tag.get('term', '') for tag in entry.get('tags', [])]

            return {
                'source_layer': self.source_layer,
                'source_name': self.source_name,
                'title': title,
                'content': content,
                'url': url,
                'published_at': published_at,
                'categories': categories,
                'symbols': []  # 추후 NER로 추출
            }

        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None

    def _parse_datetime(self, entry) -> datetime:
        """발행 시각 파싱"""
        try:
            if 'published_parsed' in entry and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
            elif 'updated_parsed' in entry and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6])
        except Exception:
            pass

        return datetime.now()

    async def fetch_full_article(self, url: str) -> Optional[str]:
        """
        전체 기사 본문 스크래핑 (RSS에 요약만 있을 때)

        Args:
            url: Article URL

        Returns:
            Full article text or None
        """
        async with self.semaphore:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    response = await client.get(url, headers=headers, timeout=10.0)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 일반적인 기사 본문 태그
                    article_body = soup.find('article') or soup.find('div', class_='article-body')

                    if article_body:
                        return article_body.get_text().strip()

                    return None

            except Exception as e:
                logger.warning(f"Failed to fetch full article from {url}: {e}")
                return None

    def get_url_hash(self, url: str) -> str:
        """URL 해시 생성 (중복 체크용)"""
        return hashlib.md5(url.encode()).hexdigest()


class LayeredRSSCollector:
    """다층적 RSS 수집기 관리자"""

    def __init__(self):
        self.layer1_feeds = []  # Core Signal
        self.layer2_feeds = []  # Sentiment & Momentum
        self.layer3_feeds = []  # Broad Impact

    def add_feed(self, feed_url: str, source_name: str, layer: int, rate_limit: int = 30):
        """피드 추가"""
        fetcher = RSSFetcher(feed_url, source_name, layer, rate_limit)

        if layer == 1:
            self.layer1_feeds.append(fetcher)
        elif layer == 2:
            self.layer2_feeds.append(fetcher)
        elif layer == 3:
            self.layer3_feeds.append(fetcher)

        logger.info(f"Added {source_name} to Layer {layer}")

    def fetch_all_layers(self) -> Dict[int, List[Dict]]:
        """모든 계층 수집"""
        results = {1: [], 2: [], 3: []}

        # Layer 1 (최우선)
        for fetcher in self.layer1_feeds:
            articles = fetcher.fetch_feed()
            results[1].extend(articles)

        # Layer 2
        for fetcher in self.layer2_feeds:
            articles = fetcher.fetch_feed()
            results[2].extend(articles)

        # Layer 3
        for fetcher in self.layer3_feeds:
            articles = fetcher.fetch_feed()
            results[3].extend(articles)

        logger.info(f"Collected: Layer1={len(results[1])}, Layer2={len(results[2])}, Layer3={len(results[3])}")
        return results
