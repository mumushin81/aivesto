from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import sys

sys.path.append('..')
from config.settings import SUPABASE_URL, SUPABASE_KEY
from database.models import RawNews, AnalyzedNews, PublishedArticle

class SupabaseClient:
    """Supabase 데이터베이스 클라이언트"""

    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")

    # ==================== Raw News Operations ====================

    def insert_raw_news(self, news: RawNews) -> Optional[str]:
        """원본 뉴스 저장"""
        try:
            result = self.client.table("news_raw").insert(news.to_dict()).execute()
            news_id = result.data[0]["id"] if result.data else None
            logger.info(f"Inserted raw news: {news.title[:50]}... (ID: {news_id})")
            return news_id
        except Exception as e:
            logger.error(f"Failed to insert raw news: {e}")
            return None

    def get_raw_news_by_url(self, url: str) -> Optional[Dict]:
        """URL로 뉴스 중복 확인"""
        try:
            result = self.client.table("news_raw")\
                .select("*")\
                .eq("url", url)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to check duplicate news: {e}")
            return None

    def get_unanalyzed_news(self, limit: int = 50) -> List[Dict]:
        """분석되지 않은 뉴스 가져오기"""
        try:
            # 24시간 이내 뉴스만
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()

            result = self.client.table("news_raw")\
                .select("*")\
                .gte("created_at", cutoff_time)\
                .limit(limit)\
                .execute()

            # 이미 분석된 뉴스 제외
            all_news = result.data
            analyzed_ids = self._get_analyzed_news_ids()

            unanalyzed = [news for news in all_news if news["id"] not in analyzed_ids]
            logger.info(f"Found {len(unanalyzed)} unanalyzed news items")
            return unanalyzed
        except Exception as e:
            logger.error(f"Failed to get unanalyzed news: {e}")
            return []

    def _get_analyzed_news_ids(self) -> set:
        """이미 분석된 뉴스 ID 목록"""
        try:
            result = self.client.table("analyzed_news")\
                .select("raw_news_id")\
                .execute()
            return {item["raw_news_id"] for item in result.data}
        except Exception as e:
            logger.error(f"Failed to get analyzed news IDs: {e}")
            return set()

    def cleanup_old_news(self):
        """24시간 이상 된 원본 뉴스 삭제"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            result = self.client.table("news_raw")\
                .delete()\
                .lt("created_at", cutoff_time)\
                .execute()
            count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {count} old news items")
        except Exception as e:
            logger.error(f"Failed to cleanup old news: {e}")

    # ==================== Analyzed News Operations ====================

    def insert_analyzed_news(self, news: AnalyzedNews) -> Optional[str]:
        """분석된 뉴스 저장"""
        try:
            result = self.client.table("analyzed_news").insert(news.to_dict()).execute()
            news_id = result.data[0]["id"] if result.data else None
            logger.info(f"Inserted analyzed news (score: {news.relevance_score}, ID: {news_id})")
            return news_id
        except Exception as e:
            logger.error(f"Failed to insert analyzed news: {e}")
            return None

    def get_high_relevance_news(self, min_score: int = 70, limit: int = 20) -> List[Dict]:
        """높은 관련성 점수의 뉴스 가져오기"""
        try:
            result = self.client.table("analyzed_news")\
                .select("*, news_raw(*)")\
                .gte("relevance_score", min_score)\
                .order("relevance_score", desc=True)\
                .limit(limit)\
                .execute()

            logger.info(f"Found {len(result.data)} high-relevance news items")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get high-relevance news: {e}")
            return []

    def get_unpublished_news_by_symbol(self, symbol: str, limit: int = 5) -> List[Dict]:
        """특정 종목 관련 미발행 뉴스"""
        try:
            # 아직 발행되지 않은 분석 뉴스
            published_ids = self._get_published_news_ids()

            result = self.client.table("analyzed_news")\
                .select("*, news_raw(*)")\
                .contains("affected_symbols", [symbol])\
                .limit(limit * 2)\
                .execute()

            unpublished = [
                news for news in result.data
                if news["id"] not in published_ids
            ][:limit]

            logger.info(f"Found {len(unpublished)} unpublished news for {symbol}")
            return unpublished
        except Exception as e:
            logger.error(f"Failed to get unpublished news for {symbol}: {e}")
            return []

    def _get_published_news_ids(self) -> set:
        """이미 발행된 뉴스 ID 목록"""
        try:
            result = self.client.table("published_articles")\
                .select("analyzed_news_ids")\
                .execute()

            all_ids = set()
            for item in result.data:
                all_ids.update(item["analyzed_news_ids"])
            return all_ids
        except Exception as e:
            logger.error(f"Failed to get published news IDs: {e}")
            return set()

    # ==================== Published Articles Operations ====================

    def insert_published_article(self, article: PublishedArticle) -> Optional[str]:
        """블로그 글 저장"""
        try:
            result = self.client.table("published_articles").insert(article.to_dict()).execute()
            article_id = result.data[0]["id"] if result.data else None
            logger.info(f"Inserted published article: {article.title[:50]}... (ID: {article_id})")
            return article_id
        except Exception as e:
            logger.error(f"Failed to insert published article: {e}")
            return None

    def get_recent_articles(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """최근 발행된 글 가져오기"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            result = self.client.table("published_articles")\
                .select("*")\
                .gte("created_at", cutoff_time)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            logger.info(f"Found {len(result.data)} recent articles")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get recent articles: {e}")
            return []
