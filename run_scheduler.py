#!/usr/bin/env python3
"""
자동화 스케줄러 - 뉴스 수집 및 분석 자동 실행
APScheduler를 사용한 주기적 파이프라인 실행
"""
import sys
sys.path.append('.')

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from loguru import logger

from pipeline.news_pipeline import NewsPipeline
from database.supabase_client import SupabaseClient


# 로그 설정
logger.add(
    "logs/scheduler_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)


def run_pipeline():
    """파이프라인 실행"""
    logger.info("="*70)
    logger.info(f"🚀 Starting scheduled pipeline run at {datetime.now()}")
    logger.info("="*70)

    try:
        # DB 연결 (선택)
        db_client = None
        try:
            db_client = SupabaseClient()
            logger.info("✅ Supabase connected")
        except Exception as e:
            logger.warning(f"⚠️  Supabase not available: {e}")
            logger.info("Running without database")

        # 파이프라인 실행
        pipeline = NewsPipeline(db_client=db_client, use_finbert=False)
        results = pipeline.run(save_to_db=(db_client is not None))

        # 결과 로깅
        stats = results['stats']
        logger.info(f"✅ Pipeline completed successfully")
        logger.info(f"  Total Articles: {stats['total_articles']}")
        logger.info(f"  High Priority: {stats['high_priority_count']}")
        logger.info(f"  Policy Signals: {stats['policy_signals']}")
        logger.info(f"  Saved to DB: {stats['saved_count']}")
        logger.info(f"  Duration: {stats['duration_seconds']}s")

        # High-priority 기사 알림
        if stats['high_priority_count'] > 0:
            logger.warning(f"🔔 {stats['high_priority_count']} high-priority signals detected!")

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    """스케줄러 메인 함수"""
    logger.info("="*70)
    logger.info("🤖 Aivesto News Pipeline Scheduler Starting")
    logger.info("="*70)

    scheduler = BlockingScheduler()

    # 스케줄 설정
    schedules = [
        {
            'trigger': CronTrigger(hour='*/1'),  # 매 시간
            'func': run_pipeline,
            'id': 'hourly_pipeline',
            'name': 'Hourly Pipeline Run',
            'replace_existing': True
        }
    ]

    # 스케줄 등록
    for schedule in schedules:
        scheduler.add_job(**schedule)
        logger.info(f"📅 Scheduled: {schedule['name']} - {schedule['trigger']}")

    logger.info("="*70)
    logger.info("✅ Scheduler started. Press Ctrl+C to exit.")
    logger.info("="*70)

    # 즉시 1회 실행 (테스트)
    logger.info("\n🔥 Running initial pipeline...")
    run_pipeline()

    # 스케줄러 시작
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 Scheduler stopped by user")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
