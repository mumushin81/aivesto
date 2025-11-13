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
from alerts.telegram_alerts import TelegramAlertService
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

        # 신호 대시보드 초기화 (프롬프트 기반 분석)
        self.signal_api = SignalAPI()
        self.email_service = EmailAlertService()
        self.telegram_service = TelegramAlertService()
        self.queue_manager = ArticleQueueManager()

        # 알림 수신자 (환경 변수에서 로드)
        self.alert_recipients = os.getenv("ALERT_RECIPIENTS", "").split(",") if os.getenv("ALERT_RECIPIENTS") else []
        self.telegram_chat_ids = os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if os.getenv("TELEGRAM_CHAT_IDS") else []

        logger.info("Job scheduler initialized (Claude Code + Local Analysis Mode)")
        if self.telegram_chat_ids:
            logger.info(f"✅ Telegram alerts enabled for {len(self.telegram_chat_ids)} chat(s)")

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

    def check_analysis_prompts_job(self):
        """📝 분석 프롬프트 생성 완료 확인"""
        logger.info("=== Checking analysis prompts ===")

        try:
            from pathlib import Path
            prompts_dir = Path("prompts/analysis")
            results_dir = Path("prompts/results")

            if prompts_dir.exists():
                prompts = list(prompts_dir.glob("*.md"))
                results = list(results_dir.glob("*.json")) if results_dir.exists() else []

                pending = len(prompts) - len(results)

                if pending > 0:
                    logger.info(f"📝 Pending analysis: {pending} prompts waiting for Claude Code")
                    logger.info(f"   Generated: {len(prompts)} | Processed: {len(results)}")
                else:
                    logger.info(f"✅ All prompts processed ({len(results)} completed)")

        except Exception as e:
            logger.error(f"Check prompts job error: {e}")

    def send_daily_digest_job(self):
        """일일 요약 이메일 & 텔레그램 발송"""
        logger.info("=== Starting daily digest job ===")

        email_sent = False
        telegram_sent = False

        # 이메일 발송
        if self.alert_recipients:
            try:
                email_sent = self.email_service.send_daily_digest(self.alert_recipients, hours=24)
                if email_sent:
                    logger.info("✅ Daily digest email sent successfully")
                else:
                    logger.warning("⚠️ Failed to send daily digest email")
            except Exception as e:
                logger.error(f"Email digest job error: {e}")
        else:
            logger.debug("No email recipients configured")

        # 텔레그램 발송
        if self.telegram_chat_ids:
            try:
                telegram_sent = self.telegram_service.send_daily_digest(self.telegram_chat_ids, hours=24)
                if telegram_sent:
                    logger.info("✅ Daily digest Telegram sent successfully")
                else:
                    logger.warning("⚠️ Failed to send daily digest Telegram")
            except Exception as e:
                logger.error(f"Telegram digest job error: {e}")
        else:
            logger.debug("No Telegram chat IDs configured")

        if email_sent or telegram_sent:
            logger.info("=== Daily digest job completed ===")
        else:
            logger.warning("=== No digest sent (no recipients configured) ===")

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

        # 분석 프롬프트 확인: 1시간마다 (Claude Code 처리 상황 확인)
        schedule.every(60).minutes.do(self.check_analysis_prompts_job)

        # 블로그 추천: 1시간마다
        schedule.every(ARTICLE_GENERATION_INTERVAL // 60).minutes.do(self.send_blog_recommendations_job)

        # 블로그 글 생성: 2시간마다
        schedule.every(ARTICLE_GENERATION_INTERVAL // 60).minutes.do(self.generate_articles_job)

        # 일일 요약: 매일 오전 9시
        schedule.every().day.at("09:00").do(self.send_daily_digest_job)

        # 데이터 정리: 매일 새벽 3시
        schedule.every().day.at("03:00").do(self.cleanup_job)

        logger.info("Schedule configured (Claude Code + Local Mode):")
        logger.info(f"  - News collection: every {NEWS_COLLECTION_INTERVAL // 60} minutes")
        logger.info(f"  - News analysis (prompt generation): every {ANALYSIS_INTERVAL // 60} minutes")
        logger.info(f"  - Check prompts status: every 60 minutes")
        logger.info(f"  - Blog recommendations: every {ARTICLE_GENERATION_INTERVAL // 60} minutes")
        logger.info(f"  - Article generation (prompt): every {ARTICLE_GENERATION_INTERVAL // 60} minutes")
        logger.info(f"  - Daily digest: daily at 09:00")
        logger.info(f"  - Cleanup: daily at 03:00")
        logger.info("")
        logger.info("💡 Workflow:")
        logger.info("   1. System generates prompts (automatic)")
        logger.info("   2. Claude Code analyzes & writes (manual)")
        logger.info("   3. Results saved to database (manual)")
        logger.info("   4. Dashboard updates (automatic)")

    def run_once(self):
        """모든 작업을 한 번 실행 (테스트용)"""
        logger.info("=== Running all jobs once ===")

        self.collect_news_job()
        time.sleep(5)

        self.analyze_news_job()
        time.sleep(5)

        self.check_analysis_prompts_job()
        time.sleep(5)

        self.send_blog_recommendations_job()
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
