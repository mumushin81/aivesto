#!/usr/bin/env python3
"""
블로그 기사당 5장 이상의 이미지 생성
부족한 이미지들을 추가로 생성
"""
import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List

# magic_book 모듈 import
magic_book_path = Path.home() / 'dev' / 'magic_book'
sys.path.insert(0, str(magic_book_path))

from dotenv import load_dotenv
from supabase import create_client
from loguru import logger
from src.midjourney import generate_images_batch_and_save

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# 각 블로그 기사별 5장의 이미지 완전 매핑
COMPLETE_ARTICLE_IMAGE_MAPPING = {
    "article_NVDA_blackwell_gpu_20251113.md": [
        {"key": "NVDA_blackwell_chip", "num": 1},
        {"key": "NVDA_ai_datacenter", "num": 2},
        {"key": "NVDA_blackwell_chip", "num": 3},  # 다른 앵글
        {"key": "NVDA_ai_datacenter", "num": 4},   # 다른 앵글
        {"key": "NVDA_blackwell_chip", "num": 5}   # 다른 앵글
    ],
    "article_NVDA_foxconn_ai_server_20251115.md": [
        {"key": "NVDA_blackwell_chip", "num": 1},
        {"key": "NVDA_ai_datacenter", "num": 2},
        {"key": "NVDA_blackwell_chip", "num": 3},
        {"key": "NVDA_ai_datacenter", "num": 4},
        {"key": "NVDA_blackwell_chip", "num": 5}
    ],
    "article_TSLA_robotaxi_fleet_20251113.md": [
        {"key": "TSLA_robotaxi", "num": 1},
        {"key": "TSLA_charging_network", "num": 2},
        {"key": "TSLA_robotaxi", "num": 3},
        {"key": "TSLA_charging_network", "num": 4},
        {"key": "TSLA_robotaxi", "num": 5}
    ],
    "article_AAPL_iphone_sales_20251113.md": [
        {"key": "AAPL_premium_iphone", "num": 1},
        {"key": "AAPL_enterprise", "num": 2},
        {"key": "AAPL_premium_iphone", "num": 3},
        {"key": "AAPL_enterprise", "num": 4},
        {"key": "AAPL_premium_iphone", "num": 5}
    ],
    "article_ADBE_creative_ai_20251113.md": [
        {"key": "ADBE_creative_cloud", "num": 1},
        {"key": "ADBE_firefly_ai", "num": 2},
        {"key": "ADBE_creative_cloud", "num": 3},
        {"key": "ADBE_firefly_ai", "num": 4},
        {"key": "ADBE_creative_cloud", "num": 5}
    ],
    "article_AMZN_aws_ai_services_20251113.md": [
        {"key": "AMZN_aws_cloud", "num": 1},
        {"key": "AMZN_ai_services", "num": 2},
        {"key": "AMZN_aws_cloud", "num": 3},
        {"key": "AMZN_ai_services", "num": 4},
        {"key": "AMZN_aws_cloud", "num": 5}
    ],
    "article_GOOGL_search_ai_20251113.md": [
        {"key": "GOOGL_search_ai", "num": 1},
        {"key": "GOOGL_advertising", "num": 2},
        {"key": "GOOGL_search_ai", "num": 3},
        {"key": "GOOGL_advertising", "num": 4},
        {"key": "GOOGL_search_ai", "num": 5}
    ],
    "article_META_enterprise_ai_20251113.md": [
        {"key": "META_business_ai", "num": 1},
        {"key": "META_llama_opensource", "num": 2},
        {"key": "META_business_ai", "num": 3},
        {"key": "META_llama_opensource", "num": 4},
        {"key": "META_business_ai", "num": 5}
    ],
    "article_MSFT_AI_office_integration_20251113.md": [
        {"key": "MSFT_copilot", "num": 1},
        {"key": "MSFT_azure_cloud", "num": 2},
        {"key": "MSFT_copilot", "num": 3},
        {"key": "MSFT_azure_cloud", "num": 4},
        {"key": "MSFT_copilot", "num": 5}
    ],
    "article_NFLX_subscriber_growth_20251113.md": [
        {"key": "NFLX_streaming", "num": 1},
        {"key": "NFLX_advertising", "num": 2},
        {"key": "NFLX_streaming", "num": 3},
        {"key": "NFLX_advertising", "num": 4},
        {"key": "NFLX_streaming", "num": 5}
    ],
    "article_UBER_profitability_expansion_20251113.md": [
        {"key": "UBER_rideshare", "num": 1},
        {"key": "UBER_eats", "num": 2},
        {"key": "UBER_rideshare", "num": 3},
        {"key": "UBER_eats", "num": 4},
        {"key": "UBER_rideshare", "num": 5}
    ]
}

def load_prompts() -> Dict:
    """AI 이미지 프롬프트 로드"""
    prompt_file = Path(__file__).parent / 'ai_image_prompts.json'
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_images_count():
    """Supabase에 이미 있는 이미지 개수 확인"""
    supabase = create_client(supabase_url, supabase_key)
    result = supabase.table('midjourney_images')\
        .select('*', count='exact')\
        .eq('image_type', 'original')\
        .execute()
    return result.count

def main():
    logger.info("=" * 80)
    logger.info("🎨 블로그 기사당 5장 이미지 생성")
    logger.info("=" * 80)

    # 기존 이미지 확인
    existing_count = get_existing_images_count()
    logger.info(f"\n📊 현재 Supabase에 저장된 원본 이미지: {existing_count}개")

    # 프롬프트 로드
    prompts_data = load_prompts()
    logger.info(f"📝 로드된 프롬프트 템플릿: {len(prompts_data)}개")

    # 필요한 고유 키 추출
    unique_keys = set()
    for article, images in COMPLETE_ARTICLE_IMAGE_MAPPING.items():
        for img in images:
            unique_keys.add(img['key'])

    logger.info(f"\n🔑 필요한 고유 이미지 키: {len(unique_keys)}개")
    logger.info(f"   {', '.join(sorted(unique_keys))}")

    # 각 키별로 필요한 개수 계산
    key_needs = {}
    for article, images in COMPLETE_ARTICLE_IMAGE_MAPPING.items():
        for img in images:
            key = img['key']
            key_needs[key] = key_needs.get(key, 0) + 1

    logger.info(f"\n📋 키별 필요 이미지 개수:")
    for key, count in sorted(key_needs.items()):
        logger.info(f"   • {key}: {count}개")

    # 총 필요 이미지 계산
    total_needed = sum(key_needs.values())
    logger.info(f"\n📊 총계:")
    logger.info(f"   • 블로그 기사: {len(COMPLETE_ARTICLE_IMAGE_MAPPING)}개")
    logger.info(f"   • 기사당 이미지: 5장")
    logger.info(f"   • 총 필요 이미지: {total_needed}개")
    logger.info(f"   • 이미 생성됨: {existing_count}개")
    logger.info(f"   • 추가 생성 필요: {max(0, total_needed - existing_count)}개")

    # Midjourney 프롬프트 준비 (가장 많이 필요한 순서대로)
    sorted_keys = sorted(key_needs.items(), key=lambda x: x[1], reverse=True)

    midjourney_prompts = []
    for key, needed_count in sorted_keys:
        if key in prompts_data:
            prompt = prompts_data[key]['midjourney_prompt']
            # 필요한 만큼 프롬프트 추가 (최대 각 3개까지)
            for i in range(min(needed_count, 3)):
                midjourney_prompts.append(prompt)
                logger.info(f"   • {key} ({i+1}/{needed_count}): {prompt[:60]}...")
        else:
            logger.warning(f"   ⚠️  프롬프트 없음: {key}")

    logger.info(f"\n🎨 생성할 Midjourney 이미지: {len(midjourney_prompts)}개")
    logger.info(f"⏱️  예상 소요 시간: {len(midjourney_prompts) * 1.5:.0f}분")

    # Midjourney 이미지 생성
    logger.info(f"\n⏳ 이미지 생성 시작...")
    results = generate_images_batch_and_save(
        prompts=midjourney_prompts,
        auto_crop=True,  # 4개 크롭 생성
        save_locally=False,
        verbose=True
    )

    logger.success(f"\n✅ 생성 완료: {len(results)}개")

    # 결과 요약
    success_count = sum(1 for r in results if r.success)
    logger.info("\n" + "=" * 80)
    logger.success(f"✅ 성공: {success_count}/{len(results)}개")
    logger.info("=" * 80)
    logger.info("\n💡 다음 단계: download_and_place_images.py 실행하여 이미지 다운로드")

if __name__ == "__main__":
    main()
