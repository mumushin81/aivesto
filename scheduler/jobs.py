import schedule
import time
from datetime import datetime
from loguru import logger
import sys
import os

sys.path.append('..')
from database.supabase_client import SupabaseClient
from collectors import FinnhubCollector, AlphaVantageCollector, RSSCollector
from analyzers import AnalysisPipeline
from writers import ArticleGenerator
from dashboard import SignalAPI
from alerts import EmailAlertService
from blogger import ArticleQueueManager
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

        # 새로운 시스템 초기화
        self.signal_api = SignalAPI()
        self.email_service = EmailAlertService()
        self.queue_manager = ArticleQueueManager()

        # 알림 수신자 (환경 변수에서 로드)
        self.alert_recipients = os.getenv("ALERT_RECIPIENTS", "").split(",") if os.getenv("ALERT_RECIPIENTS") else []

        logger.info("Job scheduler initialized with signal API, email alerts, and article queue")

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
        """뉴스 분석 작업 (자동 분석 - 모든 미분석 뉴스)"""
        logger.info("=== Starting news analysis job (AUTO MODE) ===")

        try:
            # 자동 분석: 미분석 뉴스 모두 분석 (200개씩 배치)
            analyzed_count = self.analyzer.run_analysis(limit=200)
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

    def send_urgent_alerts_job(self):
        """긴급 시그널 알림 발송 (Level 1)"""
        logger.info("=== Starting urgent alerts job ===")

        if not self.alert_recipients:
            logger.warning("No alert recipients configured - skipping email alerts")
            return

        try:
            urgent_signals = self.signal_api.get_urgent_signals(hours=1, limit=5)

            if urgent_signals:
                for signal in urgent_signals:
                    self.email_service.send_urgent_alert(signal, self.alert_recipients)
                logger.info(f"=== Sent {len(urgent_signals)} urgent alerts ===")
            else:
                logger.info("No urgent signals found")

        except Exception as e:
            logger.error(f"Urgent alerts job error: {e}")

    def send_daily_digest_job(self):
        """일일 요약 이메일 발송"""
        logger.info("=== Starting daily digest job ===")

        if not self.alert_recipients:
            logger.warning("No alert recipients configured - skipping email digest")
            return

        try:
            success = self.email_service.send_daily_digest(self.alert_recipients, hours=24)
            if success:
                logger.info("=== Daily digest sent successfully ===")
            else:
                logger.warning("Failed to send daily digest")

        except Exception as e:
            logger.error(f"Daily digest job error: {e}")

    def send_blog_recommendations_job(self):
        """블로거 글쓰기 추천 업데이트"""
        logger.info("=== Starting blog recommendations job ===")

        try:
            recommendations = self.queue_manager.get_smart_recommendations()

            if recommendations:
                logger.info(f"=== Generated blog recommendations ===")
                logger.info(f"   Tier 1 Urgent: {len(recommendations.get('tier_1_urgent', []))} signals")
                logger.info(f"   Daily Suggestions: {len(recommendations.get('daily_suggestions', []))} items")
                logger.info(f"   Trending Symbols: {len(recommendations.get('trending_symbols', []))} symbols")

        except Exception as e:
            logger.error(f"Blog recommendations job error: {e}")

    def setup_schedule(self):
        """스케줄 설정"""
        # 뉴스 수집: 15분마다
        schedule.every(NEWS_COLLECTION_INTERVAL // 60).minutes.do(self.collect_news_job)

        # 뉴스 분석: 30분마다
        schedule.every(ANALYSIS_INTERVAL // 60).minutes.do(self.analyze_news_job)

        # 긴급 알림: 15분마다 (Level 1 신호 실시간 추적)
        schedule.every(15).minutes.do(self.send_urgent_alerts_job)

        # 블로그 추천: 1시간마다
        schedule.every(ARTICLE_GENERATION_INTERVAL // 60).minutes.do(self.send_blog_recommendations_job)

        # 블로그 글 생성: 2시간마다
        schedule.every(ARTICLE_GENERATION_INTERVAL // 60).minutes.do(self.generate_articles_job)

        # 일일 요약: 매일 오전 9시
        schedule.every().day.at("09:00").do(self.send_daily_digest_job)

        # 데이터 정리: 매일 새벽 3시
        schedule.every().day.at("03:00").do(self.cleanup_job)

        logger.info("Schedule configured:")
        logger.info(f"  - News collection: every {NEWS_COLLECTION_INTERVAL // 60} minutes")
        logger.info(f"  - News analysis: every {ANALYSIS_INTERVAL // 60} minutes")
        logger.info(f"  - Urgent alerts: every 15 minutes")
        logger.info(f"  - Blog recommendations: every {ARTICLE_GENERATION_INTERVAL // 60} minutes")
        logger.info(f"  - Article generation: every {ARTICLE_GENERATION_INTERVAL // 60} minutes")
        logger.info(f"  - Daily digest: daily at 09:00")
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
