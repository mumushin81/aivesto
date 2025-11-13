from typing import List, Dict
from loguru import logger
import sys

sys.path.append('..')
from database.supabase_client import SupabaseClient
from database.models import AnalyzedNews
from analyzers.relevance_analyzer import RelevanceAnalyzer

class AnalysisPipeline:
    """뉴스 분석 파이프라인"""

    def __init__(self, db_client: SupabaseClient):
        self.db = db_client
        self.analyzer = RelevanceAnalyzer()
        logger.info("Analysis pipeline initialized")

    def run_analysis(self, limit: int = 50) -> int:
        """미분석 뉴스를 분석하고 저장"""
        try:
            # 미분석 뉴스 가져오기
            unanalyzed_news = self.db.get_unanalyzed_news(limit=limit)

            if not unanalyzed_news:
                logger.info("No unanalyzed news found")
                return 0

            logger.info(f"Found {len(unanalyzed_news)} unanalyzed news items")

            # 배치 분석
            analysis_results = self.analyzer.batch_analyze(unanalyzed_news)

            # 저장
            saved_count = 0
            for result in analysis_results:
                analyzed_news = AnalyzedNews(
                    raw_news_id=result['news_id'],
                    relevance_score=result['analysis']['relevance_score'],
                    affected_symbols=result['analysis']['affected_symbols'],
                    price_impact=result['analysis']['price_impact'],
                    importance=result['analysis']['importance'],
                    analysis={
                        'reasoning': result['analysis']['reasoning'],
                        'key_points': result['analysis']['key_points']
                    }
                )

                news_id = self.db.insert_analyzed_news(analyzed_news)
                if news_id:
                    saved_count += 1

            logger.info(f"Analysis pipeline completed: {saved_count} news items analyzed and saved")
            return saved_count

        except Exception as e:
            logger.error(f"Analysis pipeline error: {e}")
            return 0

    def get_trending_symbols(self, hours: int = 24) -> Dict[str, int]:
        """최근 트렌딩 종목 분석"""
        try:
            high_relevance_news = self.db.get_high_relevance_news(limit=100)

            symbol_counts = {}
            for news in high_relevance_news:
                for symbol in news['affected_symbols']:
                    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

            # 정렬
            trending = dict(sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True))
            logger.info(f"Trending symbols: {list(trending.keys())[:10]}")

            return trending

        except Exception as e:
            logger.error(f"Error getting trending symbols: {e}")
            return {}
