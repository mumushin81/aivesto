#!/usr/bin/env python3
"""
블로그 기사 분석 → 필요 이미지 파악 → 프롬프트 생성 → Midjourney 이미지 생성
"""
import os
import sys
import json
import re
import requests
from pathlib import Path
from typing import Dict, List, Tuple

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

# 각 블로그 기사에 필요한 5장의 이미지 (기사 내용 기반으로 세밀하게 매핑)
ARTICLE_IMAGES_5_PER_ARTICLE = {
    "article_NVDA_blackwell_gpu_20251113.md": [
        "NVDA_blackwell_chip_1.jpg",
        "NVDA_datacenter_demand_2.jpg",
        "NVDA_cuda_ecosystem_3.jpg",
        "NVDA_market_share_4.jpg",
        "NVDA_tsmc_partnership_5.jpg"
    ],
    "article_NVDA_foxconn_ai_server_20251115.md": [
        "NVDA_foxconn_factory_1.jpg",
        "NVDA_ai_server_tech_2.jpg",
        "NVDA_blackwell_production_3.jpg",
        "NVDA_server_assembly_4.jpg",
        "NVDA_taiwan_manufacturing_5.jpg"
    ],
    "article_TSLA_robotaxi_fleet_20251113.md": [
        "TSLA_robotaxi_autonomous_1.jpg",
        "TSLA_charging_network_2.jpg",
        "TSLA_fsd_technology_3.jpg",
        "TSLA_fleet_management_4.jpg",
        "TSLA_urban_deployment_5.jpg"
    ],
    "article_AAPL_iphone_sales_20251113.md": [
        "AAPL_iphone_premium_1.jpg",
        "AAPL_enterprise_2.jpg",
        "AAPL_ecosystem_integration_3.jpg",
        "AAPL_services_revenue_4.jpg",
        "AAPL_retail_strategy_5.jpg"
    ],
    "article_ADBE_creative_ai_20251113.md": [
        "ADBE_creative_cloud_1.jpg",
        "ADBE_firefly_ai_2.jpg",
        "ADBE_photoshop_ai_3.jpg",
        "ADBE_video_editing_4.jpg",
        "ADBE_designer_workflow_5.jpg"
    ],
    "article_AMZN_aws_ai_services_20251113.md": [
        "AMZN_aws_datacenter_1.jpg",
        "AMZN_ai_platform_2.jpg",
        "AMZN_bedrock_models_3.jpg",
        "AMZN_cloud_infrastructure_4.jpg",
        "AMZN_enterprise_adoption_5.jpg"
    ],
    "article_GOOGL_search_ai_20251113.md": [
        "GOOGL_search_ai_1.jpg",
        "GOOGL_ad_business_2.jpg",
        "GOOGL_gemini_integration_3.jpg",
        "GOOGL_search_evolution_4.jpg",
        "GOOGL_revenue_model_5.jpg"
    ],
    "article_META_enterprise_ai_20251113.md": [
        "META_business_tools_2.jpg",
        "META_llama_opensource_1.jpg",
        "META_ai_assistant_3.jpg",
        "META_enterprise_deployment_4.jpg",
        "META_developer_ecosystem_5.jpg"
    ],
    "article_MSFT_AI_office_integration_20251113.md": [
        "MSFT_copilot_integration_1.jpg",
        "MSFT_revenue_growth_2.jpg",
        "MSFT_office_ai_features_3.jpg",
        "MSFT_azure_openai_4.jpg",
        "MSFT_enterprise_adoption_5.jpg"
    ],
    "article_NFLX_subscriber_growth_20251113.md": [
        "NFLX_streaming_content_1.jpg",
        "NFLX_advertising_2.jpg",
        "NFLX_global_expansion_3.jpg",
        "NFLX_content_strategy_4.jpg",
        "NFLX_subscriber_tiers_5.jpg"
    ],
    "article_UBER_profitability_expansion_20251113.md": [
        "UBER_rideshare_profit_1.jpg",
        "UBER_eats_delivery_2.jpg",
        "UBER_market_expansion_3.jpg",
        "UBER_driver_network_4.jpg",
        "UBER_revenue_diversification_5.jpg"
    ]
}

# 기존 프롬프트를 재사용하되, 번호별로 약간 다른 스타일 적용
MIDJOURNEY_PROMPTS_BY_FILENAME = {
    # NVDA Blackwell GPU 기사
    "NVDA_blackwell_chip_1.jpg": "NVDA Blackwell GPU launch, cinematic 16:9 wide shot, futuristic server hall, sleek matte-black GPU core with radiant emerald energy, volumetric light rays, fine metallic textures, investment blog cover, professional photographic realism --ar 16:9 --v 6",
    "NVDA_datacenter_demand_2.jpg": "Epic NVIDIA datacenter visualization, endless server corridors, glowing H100 GPUs in emerald light, atmospheric fog, cinematic depth, tech-finance aesthetic --ar 16:9 --stylize 300 --v 6",
    "NVDA_cuda_ecosystem_3.jpg": "NVIDIA CUDA developer ecosystem, holographic code editor, green terminal windows, PyTorch TensorFlow logos, modern workspace, tech professional aesthetic --ar 16:9 --v 6",
    "NVDA_market_share_4.jpg": "AI chip market share visualization, NVIDIA 90% dominant pie chart, glowing green segment, AMD Intel smaller portions, professional business infographic --ar 16:9 --v 6",
    "NVDA_tsmc_partnership_5.jpg": "TSMC semiconductor fabrication facility, advanced chip manufacturing, clean room environment, NVIDIA logos, Taiwan tech partnership --ar 16:9 --v 6",

    # NVDA Foxconn 기사
    "NVDA_foxconn_factory_1.jpg": "Foxconn AI server production line, robotic assembly, NVIDIA GPU installation, modern Taiwan factory, industrial tech photography --ar 16:9 --v 6",
    "NVDA_ai_server_tech_2.jpg": "Next-generation AI server architecture, multiple GPU array, cooling systems, enterprise rack design, technical blueprint aesthetic --ar 16:9 --v 6",
    "NVDA_blackwell_production_3.jpg": "Blackwell GPU mass production, assembly line workers, quality control stations, high-tech manufacturing floor --ar 16:9 --v 6",
    "NVDA_server_assembly_4.jpg": "AI server rack assembly, cable management, GPU installation close-up, professional data center equipment --ar 16:9 --v 6",
    "NVDA_taiwan_manufacturing_5.jpg": "Taiwan semiconductor ecosystem, Foxconn TSMC partnership, island manufacturing hub aerial view --ar 16:9 --v 6",

    # TSLA Robotaxi 기사
    "TSLA_robotaxi_autonomous_1.jpg": "Futuristic Tesla robotaxi fleet, clean white body with crimson accents, illuminated LiDAR sensors, bustling smart city streets, motion blur conveying speed, tech-finance mood board --ar 16:9 --stylize 250 --v 6",
    "TSLA_charging_network_2.jpg": "Tesla Supercharger network visualization, futuristic charging plaza, dramatic sunset sky, red accent lights, energy flow effects, professional automotive editorial --ar 16:9 --v 6",
    "TSLA_fsd_technology_3.jpg": "Tesla Full Self-Driving visualization, neural network overlay, city navigation, sensor fusion display, autonomous tech interface --ar 16:9 --v 6",
    "TSLA_fleet_management_4.jpg": "Robotaxi fleet management dashboard, real-time GPS tracking, route optimization, modern control center --ar 16:9 --v 6",
    "TSLA_urban_deployment_5.jpg": "Tesla robotaxis deployed in urban environment, downtown streets, passenger pickups, city mobility future --ar 16:9 --v 6",

    # AAPL iPhone 기사
    "AAPL_iphone_premium_1.jpg": "Apple premium iPhone strategy visualization, minimalist showroom, glass pedestal, cool white + midnight colors, subtle gold investment cues, clean typography zone --ar 16:9 --v 6 --style raw",
    "AAPL_enterprise_2.jpg": "Apple enterprise deployment scene, sleek boardroom, MacBook Pro array, professional setting, silver and gray tones, natural window lighting --ar 16:9 --v 6",
    "AAPL_ecosystem_integration_3.jpg": "Apple ecosystem integration, iPhone MacBook iPad Watch AirPods connected, seamless handoff visualization, minimalist aesthetic --ar 16:9 --v 6",
    "AAPL_services_revenue_4.jpg": "Apple Services revenue growth, App Store iCloud Apple Music icons, subscription model visualization, financial charts --ar 16:9 --v 6",
    "AAPL_retail_strategy_5.jpg": "Apple retail store premium experience, genius bar, product displays, customer service excellence --ar 16:9 --v 6",

    # ADBE Creative AI 기사
    "ADBE_creative_cloud_1.jpg": "Adobe Creative Cloud workflow visualization, designer desk setup, multiple creative projects on screen, red accent lighting, professional creative studio vibe --ar 16:9 --v 6",
    "ADBE_firefly_ai_2.jpg": "Adobe Firefly generative AI visualization, text-to-image magic, glowing particles, purple-orange energy, creative transformation scene --ar 16:9 --stylize 400 --v 6",
    "ADBE_photoshop_ai_3.jpg": "Adobe Photoshop AI tools, generative fill demonstration, before-after comparison, professional photo editing --ar 16:9 --v 6",
    "ADBE_video_editing_4.jpg": "Adobe Premiere Pro AI video editing, timeline workflow, color grading, professional video production --ar 16:9 --v 6",
    "ADBE_designer_workflow_5.jpg": "Creative professional using Adobe suite, multi-monitor setup, Wacom tablet, coffee, artistic workspace --ar 16:9 --v 6",

    # AMZN AWS 기사
    "AMZN_aws_datacenter_1.jpg": "AWS cloud architecture concept, floating server clusters, orange accents, blue connection lines, isometric perspective, professional tech visualization --ar 16:9 --v 6",
    "AMZN_ai_platform_2.jpg": "AWS AI services visualization, multi-model platform, glowing AI orbs, orange-purple gradients, enterprise dashboard UI --ar 16:9 --v 6",
    "AMZN_bedrock_models_3.jpg": "AWS Bedrock AI marketplace, Claude Llama models, foundation model selection interface, enterprise platform --ar 16:9 --v 6",
    "AMZN_cloud_infrastructure_4.jpg": "AWS global infrastructure map, data centers worldwide, network connections, cloud service regions --ar 16:9 --v 6",
    "AMZN_enterprise_adoption_5.jpg": "Enterprise migrating to AWS cloud, business transformation, digital modernization visualization --ar 16:9 --v 6",

    # GOOGL Search AI 기사
    "GOOGL_search_ai_1.jpg": "Google AI-powered search evolution, holographic results, multicolor Google palette, AI assistant generating answers, modern interface --ar 16:9 --v 6",
    "GOOGL_ad_business_2.jpg": "Google Ads platform visualization, rising metrics, multicolor analytics, professional marketing dashboard, success indicators --ar 16:9 --v 6",
    "GOOGL_gemini_integration_3.jpg": "Google Gemini AI integrated into search, multimodal understanding, image text voice query, next-gen search --ar 16:9 --v 6",
    "GOOGL_search_evolution_4.jpg": "Evolution of Google search, traditional to AI-powered, timeline visualization, innovation progression --ar 16:9 --v 6",
    "GOOGL_revenue_model_5.jpg": "Google advertising revenue model, search ads display network, monetization strategy visualization --ar 16:9 --v 6",

    # META Enterprise AI 기사
    "META_business_tools_2.jpg": "Meta Business AI tools concept art, modern office, holographic analytics, Meta blue (#0165E1) gradients, confident executives interacting with AI assistants, soft rim lighting --ar 16:9 --v 6",
    "META_llama_opensource_1.jpg": "Llama AI visualization, digital llama creature formed by circuits, Meta blue glow, open-source code streams, community collaboration --ar 16:9 --v 6",
    "META_ai_assistant_3.jpg": "Meta AI assistant helping business professional, productivity tools, automated workflows, enterprise integration --ar 16:9 --v 6",
    "META_enterprise_deployment_4.jpg": "Meta for Business enterprise deployment, SMB adoption, business tools dashboard, professional platform --ar 16:9 --v 6",
    "META_developer_ecosystem_5.jpg": "Meta developer ecosystem, Llama open source community, API integration, development platform --ar 16:9 --v 6",

    # MSFT Office AI 기사
    "MSFT_copilot_integration_1.jpg": "Microsoft Copilot in action, Office 365 interface, AI suggestions hologram, professional workspace, Microsoft blue tones --ar 16:9 --v 6",
    "MSFT_revenue_growth_2.jpg": "Microsoft AI revenue growth chart, Copilot adoption metrics, enterprise subscription increase, financial success --ar 16:9 --v 6",
    "MSFT_office_ai_features_3.jpg": "Microsoft Office AI features, Word Excel PowerPoint Copilot, productivity enhancement visualization --ar 16:9 --v 6",
    "MSFT_azure_openai_4.jpg": "Microsoft Azure OpenAI Service, GPT-4 integration, enterprise AI platform, cloud AI infrastructure --ar 16:9 --v 6",
    "MSFT_enterprise_adoption_5.jpg": "Enterprise adopting Microsoft Copilot, Fortune 500 deployment, business transformation success --ar 16:9 --v 6",

    # NFLX Subscriber 기사
    "NFLX_streaming_content_1.jpg": "Netflix streaming ecosystem, glowing red interface, modern home theater, multiple screens, cinematic atmosphere --ar 16:9 --v 6",
    "NFLX_advertising_2.jpg": "Netflix ad platform visualization, revenue analytics, red accent graphs, professional marketing dashboard --ar 16:9 --v 6",
    "NFLX_global_expansion_3.jpg": "Netflix global expansion map, worldwide subscriber growth, international content, market penetration --ar 16:9 --v 6",
    "NFLX_content_strategy_4.jpg": "Netflix content production, original series movies, content studio, creative development --ar 16:9 --v 6",
    "NFLX_subscriber_tiers_5.jpg": "Netflix subscription tiers, pricing model, ad-supported vs premium, membership options visualization --ar 16:9 --v 6",

    # UBER Profitability 기사
    "UBER_rideshare_profit_1.jpg": "Uber rideshare network aerial view, city night lights, white car trails, black background, urban tech aesthetic --ar 16:9 --v 6",
    "UBER_eats_delivery_2.jpg": "Uber Eats delivery network, vibrant food imagery, green accent routes, urban delivery scene, professional lifestyle photography --ar 16:9 --v 6",
    "UBER_market_expansion_3.jpg": "Uber global market expansion, international cities map, growth visualization, worldwide presence --ar 16:9 --v 6",
    "UBER_driver_network_4.jpg": "Uber driver partner network, driver app interface, earnings dashboard, gig economy platform --ar 16:9 --v 6",
    "UBER_revenue_diversification_5.jpg": "Uber revenue streams diversification, rides eats freight advertising, business model evolution --ar 16:9 --v 6"
}

def download_image(url: str, save_path: Path):
    """URL에서 이미지 다운로드"""
    response = requests.get(url)
    response.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def get_first_crop_url(parent_image_id: str) -> str:
    """첫번째 크롭 URL 조회"""
    supabase = create_client(supabase_url, supabase_key)
    crop = supabase.table('midjourney_images')\
        .select('public_url')\
        .eq('parent_image_id', parent_image_id)\
        .eq('crop_position', 'top_left')\
        .limit(1)\
        .execute()

    if crop.data:
        return crop.data[0]['public_url']

    original = supabase.table('midjourney_images')\
        .select('public_url')\
        .eq('image_id', parent_image_id)\
        .single()\
        .execute()
    return original.data['public_url']

def main():
    logger.info("=" * 80)
    logger.info("🎨 블로그 기사 전체 이미지 생성 (기사당 5장)")
    logger.info("=" * 80)

    # 모든 파일명에서 고유 프롬프트 추출
    all_filenames = set()
    for filenames in ARTICLE_IMAGES_5_PER_ARTICLE.values():
        all_filenames.update(filenames)

    logger.info(f"\n📊 통계:")
    logger.info(f"   • 총 블로그 기사: {len(ARTICLE_IMAGES_5_PER_ARTICLE)}개")
    logger.info(f"   • 기사당 이미지: 5장")
    logger.info(f"   • 총 필요 이미지: {len(all_filenames)}개 (고유)")
    logger.info(f"   • 프롬프트 준비됨: {len(MIDJOURNEY_PROMPTS_BY_FILENAME)}개")

    # 프롬프트 리스트 생성
    prompts_to_generate = []
    filename_to_prompt = {}

    for filename in sorted(all_filenames):
        if filename in MIDJOURNEY_PROMPTS_BY_FILENAME:
            prompt = MIDJOURNEY_PROMPTS_BY_FILENAME[filename]
            prompts_to_generate.append(prompt)
            filename_to_prompt[filename] = prompt
            logger.info(f"   • {filename}: {prompt[:60]}...")
        else:
            logger.warning(f"   ⚠️  프롬프트 없음: {filename}")

    logger.info(f"\n🎨 생성할 이미지: {len(prompts_to_generate)}개")
    logger.info(f"⏱️  예상 소요 시간: {len(prompts_to_generate) * 1.5:.0f}분")

    # 생성 시작
    logger.info(f"\n⏳ Midjourney 이미지 생성 중...")
    results = generate_images_batch_and_save(
        prompts=prompts_to_generate,
        auto_crop=True,
        save_locally=False,
        verbose=True
    )

    logger.success(f"\n✅ 생성 완료: {len(results)}개")

    # 이미지 다운로드
    public_images_dir = Path(__file__).parent.parent / 'public' / 'images'
    public_images_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"\n📥 이미지 다운로드 중...")
    downloaded = 0

    for idx, (filename, prompt) in enumerate(filename_to_prompt.items()):
        if idx < len(results) and results[idx].success:
            try:
                image_id = results[idx].supabase_image_ids[0]
                url = get_first_crop_url(image_id)
                save_path = public_images_dir / filename
                download_image(url, save_path)
                downloaded += 1
                logger.success(f"   ✅ {filename}")
            except Exception as e:
                logger.error(f"   ❌ {filename}: {e}")

    logger.info("\n" + "=" * 80)
    logger.success(f"✅ 완료! {downloaded}/{len(prompts_to_generate)}개 이미지 다운로드")
    logger.info(f"📁 저장 위치: {public_images_dir}")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
