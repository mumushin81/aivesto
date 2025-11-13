#!/usr/bin/env python3
"""
미국 주식 뉴스 자동 분석 블로그 시스템
Stock News Automation System
"""

import sys
import argparse
from loguru import logger

# 로깅 설정
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/stock_news_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip"
)

from scheduler.jobs import JobScheduler

def main():
    parser = argparse.ArgumentParser(
        description="Stock News Automation System"
    )
    parser.add_argument(
        '--mode',
        choices=['run', 'once', 'collect', 'analyze', 'generate'],
        default='run',
        help='실행 모드 선택'
    )

    args = parser.parse_args()

    scheduler = JobScheduler()

    try:
        if args.mode == 'run':
            # 전체 시스템 실행
            logger.info("Starting Stock News Automation System")
            scheduler.run_forever()

        elif args.mode == 'once':
            # 모든 작업 1회 실행
            logger.info("Running all jobs once")
            scheduler.run_once()

        elif args.mode == 'collect':
            # 뉴스 수집만
            logger.info("Running news collection only")
            scheduler.collect_news_job()

        elif args.mode == 'analyze':
            # 뉴스 분석만
            logger.info("Running news analysis only")
            scheduler.analyze_news_job()

        elif args.mode == 'generate':
            # 블로그 글 생성만
            logger.info("Running article generation only")
            scheduler.generate_articles_job()

    except KeyboardInterrupt:
        logger.info("System stopped by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
