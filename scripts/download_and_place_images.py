#!/usr/bin/env python3
"""
Supabase에서 생성된 이미지 다운로드 및 블로그 배치
기존 파일명 패턴을 유지하면서 새로운 이미지로 교체
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# 프롬프트 키워드 → 파일명 매핑
PROMPT_TO_FILENAME = {
    "NVDA Blackwell GPU": ["NVDA_blackwell_chip_1.jpg", "NVDA_foxconn_factory_1.jpg"],
    "NVIDIA datacenter": ["NVDA_datacenter_demand_2.jpg", "NVDA_ai_server_tech_2.jpg"],
    "Tesla robotaxi": ["TSLA_robotaxi_autonomous_1.jpg"],
    "Tesla Supercharger": ["TSLA_charging_network_2.jpg"],
    "Apple premium iPhone": ["AAPL_iphone_premium_1.jpg"],
    "Apple enterprise": ["AAPL_enterprise_2.jpg"],
    "Adobe Creative Cloud": ["ADBE_creative_cloud_1.jpg"],
    "Adobe Firefly": ["ADBE_firefly_ai_2.jpg"],
    "AWS cloud architecture": ["AMZN_aws_datacenter_1.jpg"],
    "AWS AI services": ["AMZN_ai_platform_2.jpg"],
    "Google AI-powered search": ["GOOGL_search_ai_1.jpg"],
    "Google Ads platform": ["GOOGL_ad_business_2.jpg"],
    "Meta Business AI": ["META_business_tools_2.jpg"],
    "Llama AI": ["META_llama_opensource_1.jpg"],
    "Microsoft Copilot": ["MSFT_copilot_integration_1.jpg", "MSFT_revenue_growth_2.jpg"],
    "Netflix streaming": ["NFLX_streaming_content_1.jpg"],
    "Netflix ad platform": ["NFLX_advertising_2.jpg"],
    "Uber rideshare": ["UBER_rideshare_profit_1.jpg"],
    "Uber Eats": ["UBER_eats_delivery_2.jpg"]
}

def download_image(url: str, save_path: Path):
    """URL에서 이미지 다운로드"""
    response = requests.get(url)
    response.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def get_selected_crop_url(image_id: str) -> str:
    """선정된 크롭 이미지 URL 조회"""
    supabase = create_client(supabase_url, supabase_key)

    # is_selected_crop=True인 이미지 찾기
    result = supabase.table('midjourney_images')\
        .select('public_url')\
        .eq('image_id', image_id)\
        .single()\
        .execute()

    if result.data:
        return result.data['public_url']

    return None

def main():
    logger.info("=" * 80)
    logger.info("📥 생성된 이미지 다운로드 및 배치")
    logger.info("=" * 80)

    supabase = create_client(supabase_url, supabase_key)
    public_images_dir = Path(__file__).parent.parent / 'public' / 'images'
    public_images_dir.mkdir(parents=True, exist_ok=True)

    # 최근 생성된 선정 크롭 이미지 조회 (is_selected_crop=True인 것들)
    selected_crops = supabase.table('midjourney_images')\
        .select('*')\
        .contains('metadata', {'is_selected_crop': True})\
        .order('created_at', desc=True)\
        .limit(50)\
        .execute()

    logger.info(f"\n📋 총 {len(selected_crops.data)}개 선정된 크롭 이미지 발견\n")

    downloaded_count = 0
    prompt_matches = {}

    for crop_image in selected_crops.data:
        prompt = crop_image.get('prompt', '')
        image_id = crop_image['image_id']
        public_url = crop_image.get('public_url', '')

        if not public_url:
            logger.warning(f"⚠️  public_url 없음: {image_id}")
            continue

        # 프롬프트와 매칭되는 파일명 찾기
        matched_filenames = []
        for keyword, filenames in PROMPT_TO_FILENAME.items():
            if keyword.lower() in prompt.lower():
                matched_filenames = filenames
                break

        if not matched_filenames:
            logger.warning(f"⚠️  매칭되는 파일명 없음: {prompt[:50]}...")
            continue

        # 첫번째 매칭 파일명 사용
        for filename in matched_filenames:
            if filename in prompt_matches:
                continue  # 이미 다운로드됨

            try:
                save_path = public_images_dir / filename
                download_image(public_url, save_path)
                downloaded_count += 1
                prompt_matches[filename] = True
                logger.success(f"✅ {filename}")
                logger.info(f"   {prompt[:60]}...")
                break  # 하나만 다운로드

            except Exception as e:
                logger.error(f"❌ {filename} 다운로드 실패: {e}")

    logger.info("\n" + "=" * 80)
    logger.success(f"✅ 완료! {downloaded_count}개 이미지 다운로드")
    logger.info(f"📁 저장 위치: {public_images_dir}")
    logger.info("=" * 80)
    logger.info("\n💡 블로그 마크다운 파일은 이미 올바른 경로를 참조하고 있으므로 별도 수정 불필요")

if __name__ == "__main__":
    main()
