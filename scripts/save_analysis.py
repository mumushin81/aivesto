#!/usr/bin/env python3
"""
분석 결과를 Supabase에 저장하는 스크립트
Claude Code에서 생성한 JSON 파일을 읽어서 DB에 저장
"""

import sys
import json
from pathlib import Path
from loguru import logger

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.supabase_client import SupabaseClient
from database.models import AnalyzedNews, PriceImpact, Importance

def save_analysis_results(json_file: str):
    """분석 결과 JSON 파일을 읽어서 DB에 저장"""

    try:
        # JSON 파일 읽기
        with open(json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

        if not isinstance(results, list):
            logger.error("JSON file must contain an array of analysis results")
            return 0

        # Supabase 연결
        db = SupabaseClient()

        saved_count = 0
        for result in results:
            try:
                # 데이터 모델 생성
                analyzed_news = AnalyzedNews(
                    raw_news_id=result['news_id'],
                    relevance_score=result['relevance_score'],
                    affected_symbols=result['affected_symbols'],
                    price_impact=PriceImpact(result['price_impact']),
                    importance=Importance(result['importance']),
                    analysis={
                        'reasoning': result.get('reasoning', ''),
                        'key_points': result.get('key_points', [])
                    }
                )

                # DB 저장
                news_id = db.insert_analyzed_news(analyzed_news)
                if news_id:
                    saved_count += 1
                    logger.info(f"Saved analysis for news {result['news_id'][:8]}... (score: {result['relevance_score']})")

            except Exception as e:
                logger.error(f"Error saving analysis result: {e}")
                continue

        logger.info(f"Successfully saved {saved_count}/{len(results)} analysis results")
        return saved_count

    except FileNotFoundError:
        logger.error(f"File not found: {json_file}")
        return 0
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error saving analysis results: {e}")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/save_analysis.py <json_file>")
        print("Example: python scripts/save_analysis.py prompts/analysis_results_20251112_1000.json")
        sys.exit(1)

    json_file = sys.argv[1]
    count = save_analysis_results(json_file)

    if count > 0:
        print(f"\n✅ Successfully saved {count} analysis results to database")
    else:
        print("\n❌ Failed to save analysis results")
        sys.exit(1)
