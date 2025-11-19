#!/usr/bin/env python3
"""
배치 프로세싱: 모든 블로그 글에 문맥 기반 이미지 생성 및 삽입

Usage:
    python scripts/batch_process_all_articles.py
    python scripts/batch_process_all_articles.py --dry-run  # 테스트 모드
    python scripts/batch_process_all_articles.py --articles "NVDA,TSLA"  # 특정 기사만
"""
import os
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from loguru import logger

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_blog_image_pipeline import run_single_article


def find_all_articles(articles_dir: Path) -> list[Path]:
    """모든 마크다운 기사 파일 찾기"""
    articles = sorted(articles_dir.glob("article_*.md"))
    logger.info(f"📚 발견된 기사: {len(articles)}개")
    return articles


def extract_symbol_from_filename(filename: str) -> str:
    """파일명에서 주식 심볼 추출"""
    # article_NVDA_blackwell_gpu_20251113.md → NVDA
    parts = filename.replace("article_", "").split("_")
    return parts[0] if parts else "UNKNOWN"


async def process_all_articles(
    articles_dir: Path = Path("articles"),
    output_dir: Path = Path("articles_with_images"),
    workdir: Path = Path("tmp/batch_pipeline"),
    dry_run: bool = False,
    filter_symbols: list[str] = None,
    max_concurrent: int = 2,  # Discord/Midjourney rate limit 고려
):
    """모든 기사에 대해 이미지 생성 및 삽입"""

    logger.info("=" * 80)
    logger.info("🚀 배치 프로세싱 시작: 블로그 글 이미지 자동 생성")
    logger.info("=" * 80)

    # 기사 파일 찾기
    all_articles = find_all_articles(articles_dir)

    # 필터링 (특정 심볼만 처리)
    if filter_symbols:
        filter_symbols = [s.upper() for s in filter_symbols]
        all_articles = [
            a for a in all_articles
            if extract_symbol_from_filename(a.name) in filter_symbols
        ]
        logger.info(f"🔍 필터 적용: {filter_symbols}")
        logger.info(f"📝 처리할 기사: {len(all_articles)}개")

    if not all_articles:
        logger.warning("❌ 처리할 기사가 없습니다.")
        return

    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    workdir.mkdir(parents=True, exist_ok=True)

    # 통계
    stats = {
        "total": len(all_articles),
        "success": 0,
        "failed": 0,
        "skipped": 0,
    }

    # Dry-run 모드
    if dry_run:
        logger.warning("🧪 DRY-RUN 모드: 실제 이미지 생성하지 않음")
        for article in all_articles:
            symbol = extract_symbol_from_filename(article.name)
            article_id = article.stem.replace("article_", "")
            logger.info(f"  [DRY-RUN] {symbol}: {article.name}")
        return stats

    # 세마포어로 동시 처리 제한 (Midjourney rate limit)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_limit(article_path: Path):
        async with semaphore:
            return await process_single_article(
                article_path=article_path,
                output_dir=output_dir,
                workdir=workdir,
                stats=stats,
            )

    # 모든 기사 처리
    tasks = [process_with_limit(article) for article in all_articles]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 결과 집계
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"❌ {all_articles[i].name}: {result}")
            stats["failed"] += 1
        elif result:
            stats["success"] += 1

    # 최종 보고
    logger.info("=" * 80)
    logger.info("🎉 배치 프로세싱 완료!")
    logger.info(f"📊 총 {stats['total']}개 기사 중:")
    logger.info(f"  ✅ 성공: {stats['success']}개")
    logger.info(f"  ❌ 실패: {stats['failed']}개")
    logger.info(f"  ⏭️  건너뜀: {stats['skipped']}개")
    logger.info(f"📁 출력 디렉토리: {output_dir}")
    logger.info("=" * 80)

    return stats


async def process_single_article(
    article_path: Path,
    output_dir: Path,
    workdir: Path,
    stats: dict,
) -> bool:
    """단일 기사 처리"""
    try:
        symbol = extract_symbol_from_filename(article_path.name)
        article_id = article_path.stem.replace("article_", "")

        logger.info(f"\n{'='*60}")
        logger.info(f"📝 처리 중: {symbol} - {article_path.name}")
        logger.info(f"{'='*60}")

        # 파이프라인 실행
        from scripts.run_blog_image_pipeline import run_pipeline

        output_file = await run_pipeline(
            article_path=str(article_path),
            article_id=article_id,
            workdir=str(workdir / article_id),
            output_path=str(output_dir / article_path.name),
        )

        if output_file:
            logger.success(f"✅ {symbol}: 완료 → {output_file}")
            return True
        else:
            logger.warning(f"⚠️  {symbol}: 건너뜀")
            stats["skipped"] += 1
            return False

    except Exception as e:
        logger.error(f"❌ {article_path.name} 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="모든 블로그 글에 문맥 기반 이미지 생성 및 삽입"
    )
    parser.add_argument(
        "--articles-dir",
        type=Path,
        default=Path("/Users/jinxin/dev/aivesto/articles"),
        help="기사 마크다운 파일 디렉토리",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/Users/jinxin/dev/aivesto/articles_with_images"),
        help="이미지가 삽입된 기사 출력 디렉토리",
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path("/Users/jinxin/dev/aivesto/tmp/batch_pipeline"),
        help="임시 작업 디렉토리",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 처리 없이 테스트만 실행",
    )
    parser.add_argument(
        "--articles",
        type=str,
        help="처리할 심볼 (쉼표 구분, 예: NVDA,TSLA,AAPL)",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=2,
        help="최대 동시 처리 수 (Midjourney rate limit 고려)",
    )

    args = parser.parse_args()

    # 필터 파싱
    filter_symbols = None
    if args.articles:
        filter_symbols = [s.strip() for s in args.articles.split(",")]

    # 실행
    stats = asyncio.run(
        process_all_articles(
            articles_dir=args.articles_dir,
            output_dir=args.output_dir,
            workdir=args.workdir,
            dry_run=args.dry_run,
            filter_symbols=filter_symbols,
            max_concurrent=args.max_concurrent,
        )
    )

    # 종료 코드
    if stats and stats["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
