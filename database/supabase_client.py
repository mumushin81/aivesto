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

    # ==================== Investment Signal Dashboard Operations ====================

    def get_signals_by_level(self, level: int, hours: int = 24, limit: int = 50) -> List[Dict]:
        """신호 레벨별 조회"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            result = self.client.table("analyzed_news")\
                .select("*, news_raw(*)")\
                .eq("signal_level", level)\
                .gte("created_at", cutoff_time)\
                .order("relevance_score", desc=True)\
                .limit(limit)\
                .execute()

            logger.info(f"Found {len(result.data)} signals at level {level}")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get signals by level: {e}")
            return []

    def get_signals_by_symbol(self, symbol: str, hours: int = 24, limit: int = 20) -> List[Dict]:
        """종목별 신호 조회"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            result = self.client.table("analyzed_news")\
                .select("*, news_raw(*)")\
                .contains("affected_symbols", [symbol])\
                .gte("created_at", cutoff_time)\
                .order("signal_level", desc=True)\
                .order("relevance_score", desc=True)\
                .limit(limit)\
                .execute()

            logger.info(f"Found {len(result.data)} signals for {symbol}")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get signals for symbol: {e}")
            return []

    def get_trending_symbols(self, hours: int = 24, limit: int = 15) -> List[Dict]:
        """트렌딩 종목 (가장 많은 시그널) 조회"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            # 최근 분석된 뉴스 가져오기
            result = self.client.table("analyzed_news")\
                .select("affected_symbols, relevance_score, signal_level, created_at")\
                .gte("created_at", cutoff_time)\
                .order("signal_level", desc=True)\
                .order("relevance_score", desc=True)\
                .execute()

            # 종목별로 집계
            symbol_stats = {}
            for news in result.data:
                for symbol in news.get("affected_symbols", []):
                    if symbol not in symbol_stats:
                        symbol_stats[symbol] = {
                            "symbol": symbol,
                            "count": 0,
                            "avg_score": 0,
                            "urgency_count": 0
                        }
                    symbol_stats[symbol]["count"] += 1
                    symbol_stats[symbol]["avg_score"] += news.get("relevance_score", 0)
                    if news.get("signal_level") == 1:
                        symbol_stats[symbol]["urgency_count"] += 1

            # 점수 평균 계산
            for symbol in symbol_stats:
                if symbol_stats[symbol]["count"] > 0:
                    symbol_stats[symbol]["avg_score"] /= symbol_stats[symbol]["count"]

            # 신호 개수 기준으로 정렬
            trending = sorted(
                symbol_stats.values(),
                key=lambda x: (x["urgency_count"], x["count"], x["avg_score"]),
                reverse=True
            )[:limit]

            logger.info(f"Found {len(trending)} trending symbols")
            return trending

        except Exception as e:
            logger.error(f"Failed to get trending symbols: {e}")
            return []

    def get_price_impact_summary(self, hours: int = 24) -> Dict:
        """가격 영향도 요약"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            result = self.client.table("analyzed_news")\
                .select("price_impact")\
                .gte("created_at", cutoff_time)\
                .execute()

            summary = {"up": 0, "down": 0, "neutral": 0}
            for news in result.data:
                impact = news.get("price_impact", "neutral")
                if impact in summary:
                    summary[impact] += 1

            logger.info(f"Price impact summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Failed to get price impact summary: {e}")
            return {"up": 0, "down": 0, "neutral": 0}

    def get_important_symbols_today(self) -> List[Dict]:
        """오늘 주목할 종목 (Level 1-2 신호 있는 종목)"""
        try:
            cutoff_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

            result = self.client.table("analyzed_news")\
                .select("affected_symbols, signal_level, relevance_score")\
                .gte("created_at", cutoff_time)\
                .or_("signal_level.eq.1,signal_level.eq.2")\
                .execute()

            # 종목별 신호 집계
            symbols = {}
            for news in result.data:
                for symbol in news.get("affected_symbols", []):
                    if symbol not in symbols:
                        symbols[symbol] = {
                            "symbol": symbol,
                            "signals": 0,
                            "max_score": 0,
                            "urgent_count": 0
                        }
                    symbols[symbol]["signals"] += 1
                    symbols[symbol]["max_score"] = max(symbols[symbol]["max_score"], news.get("relevance_score", 0))
                    if news.get("signal_level") == 1:
                        symbols[symbol]["urgent_count"] += 1

            # 긴급 신호 > 신호 개수 기준 정렬
            important = sorted(
                symbols.values(),
                key=lambda x: (x["urgent_count"], x["signals"], x["max_score"]),
                reverse=True
            )[:10]

            logger.info(f"Found {len(important)} important symbols for today")
            return important

        except Exception as e:
            logger.error(f"Failed to get important symbols: {e}")
            return []

    def mark_signal_as_processed(self, signal_id: str) -> bool:
        """시그널 처리 표시 (향후 추가 필드)"""
        try:
            # 향후 구현: 'processed_at' 필드 추가 시 사용
            logger.info(f"Marked signal {signal_id} as processed")
            return True
        except Exception as e:
            logger.error(f"Failed to mark signal as processed: {e}")
            return False

    # ==================== Phase 6: Dashboard Real-time Data ====================

    def get_dashboard_stats(self) -> Dict:
        """대시보드 실시간 통계"""
        try:
            # 전체 기사 수
            total_result = self.client.table("analyzed_news")\
                .select("id", count="exact")\
                .execute()
            total_articles = total_result.count if hasattr(total_result, 'count') else len(total_result.data)

            # High-priority (80+점) 기사 수
            high_priority_result = self.client.table("analyzed_news")\
                .select("id", count="exact")\
                .gte("relevance_score", 80)\
                .execute()
            high_priority_count = high_priority_result.count if hasattr(high_priority_result, 'count') else len(high_priority_result.data)

            # Policy signals (has_policy_change = true) 기사 수
            policy_result = self.client.table("analyzed_news")\
                .select("id", count="exact")\
                .eq("has_policy_change", True)\
                .execute()
            policy_signals = policy_result.count if hasattr(policy_result, 'count') else len(policy_result.data)

            # 최근 1시간 수집 기사
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            last_hour_result = self.client.table("analyzed_news")\
                .select("id", count="exact")\
                .gte("created_at", one_hour_ago)\
                .execute()
            last_1h_count = last_hour_result.count if hasattr(last_hour_result, 'count') else len(last_hour_result.data)

            stats = {
                "total_articles": total_articles,
                "high_priority_count": high_priority_count,
                "policy_signals": policy_signals,
                "last_1h_count": last_1h_count,
                "last_updated": datetime.now().isoformat()
            }

            logger.info(f"Dashboard stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {
                "total_articles": 0,
                "high_priority_count": 0,
                "policy_signals": 0,
                "last_1h_count": 0,
                "last_updated": datetime.now().isoformat()
            }

    def get_articles_for_dashboard(self, limit: int = 50, min_priority: int = 0, symbol: Optional[str] = None) -> List[Dict]:
        """대시보드용 기사 목록"""
        try:
            query = self.client.table("analyzed_news")\
                .select("*, news_raw(*)")

            # 우선순위 필터
            if min_priority > 0:
                query = query.gte("relevance_score", min_priority)

            # 종목 필터
            if symbol:
                query = query.contains("affected_symbols", [symbol])

            # 최근 순으로 정렬
            result = query.order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            # 응답 데이터 정리
            articles = []
            for item in result.data:
                raw_news = item.get("news_raw", {})
                articles.append({
                    "id": item.get("id"),
                    "title": raw_news.get("title", "Untitled"),
                    "url": raw_news.get("url", ""),
                    "source": raw_news.get("source", "Unknown"),
                    "symbols": item.get("affected_symbols", []),
                    "priority_score": item.get("relevance_score", 0),
                    "sentiment": item.get("sentiment", "neutral"),
                    "sentiment_score": item.get("sentiment_score", 0.0),
                    "has_policy_change": item.get("has_policy_change", False),
                    "policy_type": item.get("policy_type", None),
                    "published_at": raw_news.get("published_at", None),
                    "collected_at": raw_news.get("created_at", None),
                    "created_at": item.get("created_at", None)
                })

            logger.info(f"Retrieved {len(articles)} articles for dashboard")
            return articles

        except Exception as e:
            logger.error(f"Failed to get articles for dashboard: {e}")
            return []

    def get_articles_by_symbol_dashboard(self, symbol: str, limit: int = 20) -> List[Dict]:
        """종목별 기사 조회 (대시보드용)"""
        return self.get_articles_for_dashboard(limit=limit, symbol=symbol)
