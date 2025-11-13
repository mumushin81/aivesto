import schedule
import time
from datetime import datetime
from loguru import logger
import sys

sys.path.append('..')
from database.supabase_client import SupabaseClient
from collectors import FinnhubCollector, AlphaVantageCollector, RSSCollector
from analyzers import AnalysisPipeline
from writers import ArticleGenerator
from config.settings import (
    NEWS_COLLECTION_INTERVAL,
    ANALYSIS_INTERVAL,
    ARTICLE_GENERATION_INTERVAL
)

class JobScheduler:
    """작업 스케줄러"""

    def __init__(self):
        self.db = SupabaseClient()
        self.collectors = [
            FinnhubCollector(self.db),
            AlphaVantageCollector(self.db),
            RSSCollector(self.db)
        ]
        self.analyzer = AnalysisPipeline(self.db)
        self.writer = ArticleGenerator(self.db)

        logger.info("Job scheduler initialized")

    def collect_news_job(self):
        """뉴스 수집 작업"""
        logger.info("=== Starting news collection job ===")

        total_collected = 0
        for collector in self.collectors:
            try:
                count = collector.collect_and_save()
                total_collected += count
            except Exception as e:
                logger.error(f"Collector error: {e}")

        logger.info(f"=== News collection completed: {total_collected} items ===")

    def analyze_news_job(self):
        """뉴스 분석 작업"""
        logger.info("=== Starting news analysis job ===")

        try:
            analyzed_count = self.analyzer.run_analysis(limit=50)
            logger.info(f"=== Analysis completed: {analyzed_count} items ===")
        except Exception as e:
            logger.error(f"Analysis job error: {e}")

    def generate_articles_job(self, tier: str = "tier_1"):
        """블로그 글 생성 작업"""
        logger.info("=== Starting article generation job ===")

        try:
            article_ids = self.writer.generate_daily_articles(tier=tier)
            logger.info(f"=== Article generation completed: {len(article_ids)} articles (Tier: {tier}) ===")
        except Exception as e:
            logger.error(f"Article generation job error: {e}")

    def cleanup_job(self):
        """오래된 데이터 정리 작업"""
        logger.info("=== Starting cleanup job ===")

        try:
            self.db.cleanup_old_news()
            logger.info("=== Cleanup completed ===")
        except Exception as e:
            logger.error(f"Cleanup job error: {e}")

    def setup_schedule(self):
        """스케줄 설정"""
        # 뉴스 수집: 15분마다
        schedule.every(NEWS_COLLECTION_INTERVAL // 60).minutes.do(self.collect_news_job)

        # 뉴스 분석: 30분마다
        schedule.every(ANALYSIS_INTERVAL // 60).minutes.do(self.analyze_news_job)

        # 블로그 글 생성: 1시간마다
        schedule.every(ARTICLE_GENERATION_INTERVAL // 60).minutes.do(self.generate_articles_job)

        # 데이터 정리: 매일 새벽 3시
        schedule.every().day.at("03:00").do(self.cleanup_job)

        logger.info("Schedule configured:")
        logger.info(f"  - News collection: every {NEWS_COLLECTION_INTERVAL // 60} minutes")
        logger.info(f"  - News analysis: every {ANALYSIS_INTERVAL // 60} minutes")
        logger.info(f"  - Article generation: every {ARTICLE_GENERATION_INTERVAL // 60} minutes")
        logger.info(f"  - Cleanup: daily at 03:00")

    def run_once(self):
        """모든 작업을 한 번 실행 (테스트용)"""
        logger.info("=== Running all jobs once ===")

        self.collect_news_job()
        time.sleep(5)

        self.analyze_news_job()
        time.sleep(5)

        self.generate_articles_job()
        time.sleep(5)

        self.cleanup_job()

        logger.info("=== All jobs completed ===")

    def run_forever(self):
        """스케줄러 무한 실행"""
        self.setup_schedule()

        # 시작 시 한 번 실행
        logger.info("Running initial job cycle...")
        self.run_once()

        # 무한 루프
        logger.info("Starting scheduler loop...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
