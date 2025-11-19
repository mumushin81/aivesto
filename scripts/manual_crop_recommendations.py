#!/usr/bin/env python3
"""
수동으로 분석한 크롭 이미지 추천 결과를 DB에 저장
Claude Code의 수동 분석 결과 기반
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    logger.error("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
    logger.info("Please add these to your .env file:")
    logger.info("  SUPABASE_URL=https://your-project.supabase.co")
    logger.info("  SUPABASE_SERVICE_KEY=your_service_role_key")
    logger.info("")
    logger.info("⚠️  Note: This script requires SERVICE_KEY (not ANON_KEY) for write operations")
    raise ValueError("Missing required Supabase credentials in environment variables")

# 수동 분석 결과
MANUAL_RECOMMENDATIONS = {
    "f5abc6f2b048": {  # Futuristic NVIDIA GPU chip
        "best_crop": "bottom_right",
        "scores": {
            "top_left": 85,
            "top_right": 70,
            "bottom_left": 75,
            "bottom_right": 95
        },
        "reasoning": "bottom_right crop provides the best composition with the NVIDIA chip perfectly centered. The glowing green circuit traces create dramatic visual impact while maintaining professional tech aesthetic. Clear branding visibility and optimal lighting make it ideal for blog thumbnail."
    },
    "023ca13022da": {  # Technical architecture diagram
        "best_crop": "top_left",
        "scores": {
            "top_left": 90,
            "top_right": 75,
            "bottom_left": 80,
            "bottom_right": 70
        },
        "reasoning": "top_left crop captures the most complete view of the GPU architecture diagram with clear component labels and clean white background. The isometric perspective is well-balanced and provides maximum technical detail visibility."
    },
    "66efb1363bdc": {  # Professional technology concept
        "best_crop": "bottom_left",
        "scores": {
            "top_left": 80,
            "top_right": 70,
            "bottom_left": 92,
            "bottom_right": 75
        },
        "reasoning": "bottom_left crop showcases the green and black color palette most effectively with strong contrast and modern digital aesthetic. The composition creates professional corporate tech feel ideal for blog header."
    }
}

def update_all_recommendations():
    """모든 추천 결과를 DB에 업데이트"""
    supabase = create_client(supabase_url, supabase_key)

    logger.info("=" * 60)
    logger.info("📝 수동 분석 결과 DB 저장")
    logger.info("=" * 60)

    for image_id, recommendation in MANUAL_RECOMMENDATIONS.items():
        try:
            metadata = {
                "ai_recommendation": {
                    "best_crop": recommendation["best_crop"],
                    "scores": recommendation["scores"],
                    "reasoning": recommendation["reasoning"],
                    "analyzed_at": "2025-11-16T15:47:00Z",
                    "analysis_method": "manual_claude_code"
                }
            }

            result = supabase.table('midjourney_images')\
                .update({"metadata": metadata})\
                .eq('image_id', image_id)\
                .execute()

            logger.success(f"✅ {image_id[:12]}... → {recommendation['best_crop']} (점수: {recommendation['scores'][recommendation['best_crop']]})")

        except Exception as e:
            logger.error(f"❌ {image_id[:12]}... 저장 실패: {e}")

    logger.info("=" * 60)
    logger.success("✅ 모든 추천 정보 저장 완료!")
    logger.info("=" * 60)

if __name__ == "__main__":
    update_all_recommendations()
