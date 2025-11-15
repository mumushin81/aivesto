#!/usr/bin/env python3
"""
Add image placeholders to blog articles
Inserts image markdown into articles and creates a guide for downloading actual images
"""

import os
from pathlib import Path
import csv

# Article image configurations
ARTICLE_IMAGES = {
    "article_AAPL_iphone_sales_20251113.md": [
        {
            "query": "iphone pro premium smartphone technology",
            "caption": "iPhone Pro 모델의 프리미엄 기능이 평균 판매가 상승을 이끌고 있습니다",
            "position_after": "평균판매가가 $780에서 $850으로 9% 상승했다는 것입니다.",
            "filename": "AAPL_iphone_premium_1.jpg"
        },
        {
            "query": "business professionals using smartphones office",
            "caption": "기업 시장에서 iPhone 채택이 증가하며 안정적인 매출을 제공합니다",
            "position_after": "기업용은 개인용보다 훨씬 비쌉니다.",
            "filename": "AAPL_enterprise_2.jpg"
        }
    ],
    "article_ADBE_creative_ai_20251113.md": [
        {
            "query": "designer working on computer creative software",
            "caption": "Adobe Firefly AI가 전문 디자이너의 작업 흐름을 혁신하고 있습니다",
            "position_after": "몇 초 안에 끝납니다.",
            "filename": "ADBE_designer_ai_1.jpg"
        },
        {
            "query": "digital art creative tools photoshop",
            "caption": "생성형 AI 기능이 모든 Adobe 창작 도구에 통합되었습니다",
            "position_after": "AI가 자동으로 생성합니다.",
            "filename": "ADBE_creative_tools_2.jpg"
        }
    ],
    "article_AMZN_aws_ai_services_20251113.md": [
        {
            "query": "data center servers cloud computing technology",
            "caption": "AWS AI 서비스가 클라우드 인프라 마진율을 크게 개선하고 있습니다",
            "position_after": "AI 서비스는 50-60% 마진입니다.",
            "filename": "AMZN_aws_datacenter_1.jpg"
        },
        {
            "query": "artificial intelligence neural network technology",
            "caption": "멀티 모델 전략으로 다양한 AI 모델을 제공하는 AWS",
            "position_after": "고객이 모델을 선택할 수 있습니다.",
            "filename": "AMZN_ai_multimodel_2.jpg"
        }
    ],
    "article_GOOGL_search_ai_20251113.md": [
        {
            "query": "person searching on smartphone google",
            "caption": "Google AI 오버뷰가 검색 경험을 완전히 바꾸고 있습니다",
            "position_after": "80%의 질문에 즉시 답변합니다.",
            "filename": "GOOGL_ai_search_1.jpg"
        },
        {
            "query": "digital advertising analytics dashboard",
            "caption": "AI 검색으로 광고 체류 시간과 CPM이 모두 증가했습니다",
            "position_after": "광고 CPM도 15-20% 상승했습니다.",
            "filename": "GOOGL_advertising_2.jpg"
        }
    ],
    "article_META_enterprise_ai_20251113.md": [
        {
            "query": "social media business communication instagram facebook",
            "caption": "Meta Business AI가 5억 비즈니스 사용자를 대상으로 출시되었습니다",
            "position_after": "전환 장벽이 낮다는 뜻입니다.",
            "filename": "META_business_ai_1.jpg"
        },
        {
            "query": "customer service chatbot ai automation",
            "caption": "AI가 자동으로 고객 메시지에 응답하고 판매를 최적화합니다",
            "position_after": "시간대, 타겟층, 예산을 AI가 조정합니다.",
            "filename": "META_automation_2.jpg"
        }
    ],
    "article_MSFT_AI_office_integration_20251113.md": [
        {
            "query": "office worker using microsoft teams computer",
            "caption": "Microsoft 365 Copilot이 업무 생산성을 혁신하고 있습니다",
            "position_after": "일상 업무가 완전히 바뀌고 있습니다.",
            "filename": "MSFT_copilot_office_1.jpg"
        },
        {
            "query": "business analytics growth chart dashboard",
            "caption": "AI 통합으로 Office 365 구독료가 상승하며 수익성이 개선됩니다",
            "position_after": "월 추가 수익은 $120억입니다.",
            "filename": "MSFT_revenue_growth_2.jpg"
        }
    ],
    "article_NFLX_subscriber_growth_20251113.md": [
        {
            "query": "people watching streaming content tv couch",
            "caption": "Netflix 광고 요금제가 가격 민감 고객을 유입시키고 있습니다",
            "position_after": "전체 신규 가입자의 45%를 차지합니다.",
            "filename": "NFLX_streaming_subscribers_1.jpg"
        },
        {
            "query": "mobile video advertising smartphone",
            "caption": "광고 사업이 새로운 수익원으로 부상하고 있습니다",
            "position_after": "광고 매출은 $20억에 도달할 것입니다.",
            "filename": "NFLX_advertising_2.jpg"
        }
    ],
    "article_NVDA_blackwell_gpu_20251113.md": [
        {
            "query": "nvidia gpu chip microprocessor technology",
            "caption": "NVIDIA Blackwell GPU가 AI 성능을 5배 향상시켰습니다",
            "position_after": "5배 빠른 AI 학습이 가능합니다.",
            "filename": "NVDA_blackwell_chip_1.jpg"
        },
        {
            "query": "data center servers racks technology",
            "caption": "클라우드 3사가 Blackwell GPU를 대량 구매하고 있습니다",
            "position_after": "합계 $600억 이상의 GPU를 구매할 계획입니다.",
            "filename": "NVDA_datacenter_demand_2.jpg"
        }
    ],
    "article_NVDA_foxconn_ai_server_20251115.md": [
        {
            "query": "factory manufacturing technology electronics",
            "caption": "Foxconn의 AI 서버 매출이 전년 대비 200% 증가했습니다",
            "position_after": "AI 서버 매출은 전년 대비 무려 200% 증가했다는 것입니다.",
            "filename": "NVDA_foxconn_factory_1.jpg"
        },
        {
            "query": "server room data center technology",
            "caption": "AI 서버 조립 기술의 복잡성이 높은 마진율을 만듭니다",
            "position_after": "조립 난이도가 일반 서버의 2배 이상이라는 뜻입니다.",
            "filename": "NVDA_ai_server_tech_2.jpg"
        }
    ],
    "article_TSLA_robotaxi_fleet_20251113.md": [
        {
            "query": "self driving autonomous car technology",
            "caption": "Tesla가 2026년 상반기 로보택시 서비스를 시작합니다",
            "position_after": "인간 운전보다 10배 더 안전하다고 주장합니다.",
            "filename": "TSLA_robotaxi_autonomous_1.jpg"
        },
        {
            "query": "electric vehicle charging station network",
            "caption": "Tesla의 충전 인프라가 로보택시 경쟁 우위를 만듭니다",
            "position_after": "경쟁사들은 충전 인프라가 부족합니다.",
            "filename": "TSLA_charging_network_2.jpg"
        }
    ],
    "article_UBER_profitability_expansion_20251113.md": [
        {
            "query": "uber ride sharing city transportation",
            "caption": "Uber가 처음으로 연간 흑자를 달성했습니다",
            "position_after": "처음으로 연간 흑자를 기록할 것으로 예상됩니다.",
            "filename": "UBER_rideshare_profit_1.jpg"
        },
        {
            "query": "food delivery service mobile app",
            "caption": "Uber Eats가 전체 매출의 42%를 차지하며 성장을 견인합니다",
            "position_after": "전체 매출의 42%를 차지합니다.",
            "filename": "UBER_eats_delivery_2.jpg"
        }
    ]
}


def insert_image_into_article(article_path: Path, image_info: dict) -> bool:
    """Insert image markdown into article after specific text"""
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        position_text = image_info["position_after"]
        if position_text not in content:
            print(f"  ✗ Warning: Position text not found in {article_path.name}")
            print(f"     Looking for: {position_text[:50]}...")
            return False

        # Create image markdown
        image_md = f"\n\n![{image_info['caption']}](../public/images/{image_info['filename']})\n*{image_info['caption']}*\n"

        # Insert image after the position text
        content = content.replace(
            position_text,
            position_text + image_md
        )

        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Inserted image into {article_path.name}")
        return True

    except Exception as e:
        print(f"  ✗ Failed to insert image into {article_path.name}: {e}")
        return False


def generate_image_download_guide(output_path: Path, images_config: dict):
    """Generate CSV guide for downloading images"""
    rows = []
    for article, images in images_config.items():
        for img in images:
            rows.append({
                'Article': article,
                'Filename': img['filename'],
                'Search Query': img['query'],
                'Caption': img['caption'],
                'Download Link': f"https://www.pexels.com/search/{img['query'].replace(' ', '%20')}/",
                'Status': 'Pending'
            })

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Article', 'Filename', 'Search Query', 'Caption', 'Download Link', 'Status'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Generated image download guide: {output_path}")
    print(f"  → Open this CSV to see which images to download from Pexels.com")


def main():
    """Main function to add image placeholders to all articles"""
    project_root = Path(__file__).parent.parent
    articles_dir = project_root / "articles"
    images_dir = project_root / "public" / "images"
    guide_path = project_root / "IMAGE_DOWNLOAD_GUIDE.csv"

    # Create images directory
    images_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Adding image placeholders to blog articles")
    print("=" * 60)

    total_images = 0
    successful_insertions = 0

    # Process each article
    for article_filename, images in ARTICLE_IMAGES.items():
        article_path = articles_dir / article_filename

        if not article_path.exists():
            print(f"\n⚠ Article not found: {article_filename}")
            continue

        print(f"\n📄 Processing: {article_filename}")
        print(f"   Images to add: {len(images)}")

        for img_info in images:
            total_images += 1
            if insert_image_into_article(article_path, img_info):
                successful_insertions += 1

    # Generate download guide
    generate_image_download_guide(guide_path, ARTICLE_IMAGES)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total image placeholders: {total_images}")
    print(f"Successfully inserted: {successful_insertions}")
    print(f"Images directory: {images_dir}")
    print(f"\n📝 Next steps:")
    print(f"   1. Open IMAGE_DOWNLOAD_GUIDE.csv")
    print(f"   2. Download images from Pexels.com using the search queries")
    print(f"   3. Save images to public/images/ with the specified filenames")
    print(f"   4. Run: python3 scripts/generate_static_blog.py")

    if successful_insertions == total_images:
        print("\n✅ All image placeholders added successfully!")
        return 0
    else:
        print(f"\n⚠ Some insertions failed ({total_images - successful_insertions} failed)")
        return 1


if __name__ == "__main__":
    exit(main())
