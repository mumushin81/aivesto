from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from loguru import logger
import sys

sys.path.append('..')
from database.models import RawNews
from database.supabase_client import SupabaseClient

class BaseCollector(ABC):
    """뉴스 수집기 기본 클래스"""

    def __init__(self, db_client: SupabaseClient):
        self.db = db_client
        self.source_name = self.__class__.__name__

    @abstractmethod
    def fetch_news(self) -> List[RawNews]:
        """뉴스를 수집하는 메서드 (각 수집기에서 구현)"""
        pass

    def collect_and_save(self) -> int:
        """뉴스를 수집하고 저장"""
        try:
            logger.info(f"Starting news collection from {self.source_name}")
            news_items = self.fetch_news()

            saved_count = 0
            for news in news_items:
                # 중복 확인
                existing = self.db.get_raw_news_by_url(news.url)
                if existing:
                    logger.debug(f"Duplicate news skipped: {news.url}")
                    continue

                # 저장
                news_id = self.db.insert_raw_news(news)
                if news_id:
                    saved_count += 1

            logger.info(f"{self.source_name} collected {saved_count} new news items")
            return saved_count

        except Exception as e:
            logger.error(f"Error in {self.source_name} collector: {e}")
            return 0

    def extract_symbols_from_text(self, text: str, tracked_symbols: List[str]) -> List[str]:
        """텍스트에서 주식 심볼 추출"""
        found_symbols = []
        text_upper = text.upper()

        for symbol in tracked_symbols:
            # 심볼이 단어 경계에 있는지 확인
            if f" {symbol} " in f" {text_upper} " or f"${symbol}" in text_upper:
                found_symbols.append(symbol)

        return found_symbols
