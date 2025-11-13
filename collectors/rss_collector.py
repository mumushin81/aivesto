import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
from loguru import logger
import sys

sys.path.append('..')
from config.settings import RSS_FEEDS, TRACKED_SYMBOLS
from database.models import RawNews
from collectors.base import BaseCollector

class RSSCollector(BaseCollector):
    """RSS 피드를 사용한 뉴스 수집기"""

    def __init__(self, db_client):
        super().__init__(db_client)
        self.feeds = RSS_FEEDS
        logger.info(f"RSS collector initialized with {len(self.feeds)} feeds")

    def fetch_news(self) -> List[RawNews]:
        """RSS 피드에서 뉴스 수집"""
        news_items = []

        for feed_config in self.feeds:
            feed_name = feed_config['name']
            feed_url = feed_config['url']
            category = feed_config.get('category', 'general')

            try:
                logger.info(f"Fetching RSS feed: {feed_name}")
                feed_news = self._parse_feed(feed_url, feed_name, category)
                news_items.extend(feed_news)

            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_name}: {e}")
                continue

        return news_items

    def _parse_feed(self, feed_url: str, feed_name: str, category: str) -> List[RawNews]:
        """RSS 피드 파싱"""
        news_items = []

        try:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_name}")
                return news_items

            yesterday = datetime.now() - timedelta(days=1)

            for entry in feed.entries:
                try:
                    # 발행 시간 파싱
                    published_at = self._parse_date(entry)
                    if not published_at or published_at < yesterday:
                        continue

                    # 제목과 요약
                    title = entry.get('title', '').strip()
                    summary = entry.get('summary', entry.get('description', '')).strip()

                    # HTML 태그 제거
                    summary = self._clean_html(summary)

                    # URL
                    url = entry.get('link', '')

                    if not title or not url:
                        continue

                    # 전체 콘텐츠 시도 (선택적)
                    content = self._fetch_full_content(url, summary)

                    # 주식 심볼 추출
                    full_text = f"{title} {content}"
                    symbols = self.extract_symbols_from_text(full_text, TRACKED_SYMBOLS)

                    news = RawNews(
                        source=feed_name,
                        title=title,
                        url=url,
                        content=content,
                        published_at=published_at,
                        symbols=symbols,
                        metadata={
                            "category": category,
                            "tags": [tag.term for tag in entry.get('tags', [])],
                            "author": entry.get('author', ''),
                            "summary": summary[:500]
                        }
                    )
                    news_items.append(news)

                except Exception as e:
                    logger.error(f"Error parsing RSS entry: {e}")
                    continue

        except Exception as e:
            logger.error(f"RSS feed parsing error: {e}")

        return news_items

    def _parse_date(self, entry) -> datetime:
        """RSS 엔트리에서 날짜 파싱"""
        try:
            # published_parsed 또는 updated_parsed 사용
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6])
            else:
                # 문자열 파싱 시도
                date_str = entry.get('published', entry.get('updated', ''))
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.debug(f"Date parsing error: {e}")

        return None

    def _clean_html(self, html_text: str) -> str:
        """HTML 태그 제거"""
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except:
            return html_text

    def _fetch_full_content(self, url: str, fallback: str = "") -> str:
        """전체 기사 내용 가져오기 (선택적)"""
        try:
            # 시간 제한이 있으므로 일부 소스만 시도
            if "yahoo" in url or "reuters" in url:
                response = requests.get(url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # 일반적인 기사 본문 태그
                    article = soup.find('article')
                    if article:
                        return article.get_text(separator=' ', strip=True)[:5000]

                    # 다른 시도
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        text = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                        return text[:5000]

        except Exception as e:
            logger.debug(f"Full content fetch failed for {url}: {e}")

        return fallback
