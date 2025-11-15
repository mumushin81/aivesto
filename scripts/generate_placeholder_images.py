#!/usr/bin/env python3
"""
Generate professional placeholder images for blog articles
Creates gradient background images with company branding
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Image configurations with company colors
IMAGE_CONFIGS = {
    # Apple images
    "AAPL_iphone_premium_1.jpg": {
        "title": "iPhone Pro Premium",
        "subtitle": "프리미엄 전략 성공",
        "gradient": [(0, 0, 0), (64, 64, 64)]  # Black gradient
    },
    "AAPL_enterprise_2.jpg": {
        "title": "Enterprise Market",
        "subtitle": "기업 시장 성장",
        "gradient": [(40, 40, 40), (100, 100, 100)]
    },

    # Adobe images
    "ADBE_designer_ai_1.jpg": {
        "title": "Adobe Firefly AI",
        "subtitle": "디자이너 생산성 혁신",
        "gradient": [(237, 28, 36), (255, 127, 39)]  # Adobe red to orange
    },
    "ADBE_creative_tools_2.jpg": {
        "title": "Creative Cloud",
        "subtitle": "AI 통합 창작 도구",
        "gradient": [(49, 0, 128), (120, 81, 169)]
    },

    # Amazon AWS images
    "AMZN_aws_datacenter_1.jpg": {
        "title": "AWS Data Center",
        "subtitle": "클라우드 인프라",
        "gradient": [(35, 47, 62), (255, 153, 0)]  # AWS colors
    },
    "AMZN_ai_multimodel_2.jpg": {
        "title": "Multi-Model AI",
        "subtitle": "다양한 AI 모델 제공",
        "gradient": [(22, 25, 31), (232, 119, 34)]
    },

    # Google images
    "GOOGL_ai_search_1.jpg": {
        "title": "Google AI Overview",
        "subtitle": "검색 패러다임 전환",
        "gradient": [(66, 133, 244), (219, 68, 55)]  # Google blue to red
    },
    "GOOGL_advertising_2.jpg": {
        "title": "Digital Advertising",
        "subtitle": "광고 수익 증가",
        "gradient": [(15, 157, 88), (244, 180, 0)]  # Google green to yellow
    },

    # Meta images
    "META_business_ai_1.jpg": {
        "title": "Meta Business AI",
        "subtitle": "5억 비즈니스 사용자",
        "gradient": [(0, 102, 255), (0, 153, 255)]  # Meta blue
    },
    "META_automation_2.jpg": {
        "title": "AI Automation",
        "subtitle": "자동 고객 응대",
        "gradient": [(0, 119, 255), (51, 153, 255)]
    },

    # Microsoft images
    "MSFT_copilot_office_1.jpg": {
        "title": "Microsoft 365 Copilot",
        "subtitle": "업무 생산성 혁신",
        "gradient": [(0, 120, 212), (0, 164, 239)]  # Microsoft blue
    },
    "MSFT_revenue_growth_2.jpg": {
        "title": "Revenue Growth",
        "subtitle": "구독료 상승",
        "gradient": [(0, 103, 192), (16, 124, 16)]
    },

    # Netflix images
    "NFLX_streaming_subscribers_1.jpg": {
        "title": "Netflix Streaming",
        "subtitle": "광고 요금제 성장",
        "gradient": [(229, 9, 20), (139, 0, 0)]  # Netflix red
    },
    "NFLX_advertising_2.jpg": {
        "title": "Advertising Business",
        "subtitle": "새로운 수익원",
        "gradient": [(184, 0, 0), (85, 0, 0)]
    },

    # NVIDIA Blackwell images
    "NVDA_blackwell_chip_1.jpg": {
        "title": "NVIDIA Blackwell GPU",
        "subtitle": "AI 성능 5배 향상",
        "gradient": [(118, 185, 0), (0, 128, 0)]  # NVIDIA green
    },
    "NVDA_datacenter_demand_2.jpg": {
        "title": "Data Center Demand",
        "subtitle": "대량 구매 진행",
        "gradient": [(0, 153, 0), (0, 102, 0)]
    },

    # NVIDIA Foxconn images
    "NVDA_foxconn_factory_1.jpg": {
        "title": "Foxconn AI Server",
        "subtitle": "매출 200% 증가",
        "gradient": [(76, 175, 80), (56, 142, 60)]
    },
    "NVDA_ai_server_tech_2.jpg": {
        "title": "AI Server Technology",
        "subtitle": "조립 기술 복잡성",
        "gradient": [(67, 160, 71), (46, 125, 50)]
    },

    # Tesla images
    "TSLA_robotaxi_autonomous_1.jpg": {
        "title": "Tesla Robotaxi",
        "subtitle": "완전 자율주행",
        "gradient": [(220, 38, 38), (120, 20, 20)]  # Tesla red
    },
    "TSLA_charging_network_2.jpg": {
        "title": "Charging Network",
        "subtitle": "인프라 경쟁 우위",
        "gradient": [(204, 0, 0), (139, 0, 0)]
    },

    # Uber images
    "UBER_rideshare_profit_1.jpg": {
        "title": "Uber Profitability",
        "subtitle": "첫 연간 흑자 달성",
        "gradient": [(0, 0, 0), (50, 50, 50)]  # Uber black
    },
    "UBER_eats_delivery_2.jpg": {
        "title": "Uber Eats",
        "subtitle": "매출 42% 기여",
        "gradient": [(5, 150, 105), (0, 100, 70)]  # Uber green
    }
}


def create_gradient_image(width, height, color1, color2):
    """Create a vertical gradient image"""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def add_overlay_pattern(img):
    """Add subtle overlay pattern to image (no text)"""
    width, height = img.size

    # Create a subtle radial gradient overlay for visual interest
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Add subtle circular pattern in center for depth
    center_x, center_y = width // 2, height // 2
    max_radius = min(width, height) // 2

    for i in range(5):
        radius = max_radius - (i * 100)
        alpha = 5 + (i * 2)  # Very subtle
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=None,
            outline=(255, 255, 255, alpha),
            width=2
        )

    # Blend overlay with original image
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    return img.convert('RGB')


def generate_all_images(output_dir):
    """Generate all placeholder images"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generating placeholder images for blog articles")
    print("=" * 60)

    total = len(IMAGE_CONFIGS)
    success = 0

    for filename, config in IMAGE_CONFIGS.items():
        try:
            print(f"\n📸 Creating: {filename}")
            print(f"   Colors: {config['gradient']}")

            # Create gradient background
            img = create_gradient_image(1200, 800, config['gradient'][0], config['gradient'][1])

            # Add subtle overlay pattern (no text)
            img = add_overlay_pattern(img)

            # Save image
            filepath = output_dir / filename
            img.save(filepath, 'JPEG', quality=92)

            print(f"   ✓ Saved: {filepath}")
            success += 1

        except Exception as e:
            print(f"   ✗ Failed: {e}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total images: {total}")
    print(f"Successfully created: {success}")
    print(f"Output directory: {output_dir}")

    if success == total:
        print("\n✅ All images created successfully!")
        return 0
    else:
        print(f"\n⚠ Some images failed ({total - success} failed)")
        return 1


if __name__ == "__main__":
    import sys
    project_root = Path(__file__).parent.parent
    images_dir = project_root / "public" / "images"
    sys.exit(generate_all_images(images_dir))
