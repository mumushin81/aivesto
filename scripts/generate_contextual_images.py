#!/usr/bin/env python3
"""
Generate contextual images for blog articles that help readers understand the content.
Each image represents the specific topic discussed in the article.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Company brand colors
COMPANY_COLORS = {
    'AAPL': {'primary': (0, 0, 0), 'secondary': (147, 147, 147)},      # Apple: Black & Gray
    'ADBE': {'primary': (237, 29, 36), 'secondary': (255, 127, 130)},  # Adobe: Red
    'AMZN': {'primary': (255, 153, 0), 'secondary': (35, 47, 62)},     # Amazon: Orange & Dark
    'GOOGL': {'primary': (66, 133, 244), 'secondary': (234, 67, 53)},  # Google: Blue & Red
    'META': {'primary': (0, 120, 255), 'secondary': (0, 180, 255)},    # Meta: Blue
    'MSFT': {'primary': (0, 120, 212), 'secondary': (125, 125, 125)},  # Microsoft: Blue & Gray
    'NFLX': {'primary': (229, 9, 20), 'secondary': (0, 0, 0)},         # Netflix: Red & Black
    'NVDA': {'primary': (118, 185, 0), 'secondary': (0, 0, 0)},        # NVIDIA: Green & Black
    'TSLA': {'primary': (204, 0, 0), 'secondary': (51, 51, 51)},       # Tesla: Red & Dark Gray
    'UBER': {'primary': (0, 0, 0), 'secondary': (255, 255, 255)},      # Uber: Black & White
}

# Image definitions with visual concepts
IMAGE_DEFINITIONS = {
    # Apple
    'AAPL_iphone_premium_1.jpg': {
        'symbol': 'AAPL',
        'icon': '📱',
        'title': 'iPhone Pro',
        'subtitle': 'Premium Features',
        'elements': ['Camera', 'Display', 'Performance']
    },
    'AAPL_enterprise_2.jpg': {
        'symbol': 'AAPL',
        'icon': '🏢',
        'title': 'Enterprise',
        'subtitle': 'Business Adoption',
        'elements': ['Security', 'Management', 'Integration']
    },

    # Adobe
    'ADBE_creative_cloud_1.jpg': {
        'symbol': 'ADBE',
        'icon': '🎨',
        'title': 'Creative Cloud',
        'subtitle': 'Designer Workflow',
        'elements': ['Photoshop', 'Illustrator', 'Premiere']
    },
    'ADBE_firefly_ai_2.jpg': {
        'symbol': 'ADBE',
        'icon': '✨',
        'title': 'Firefly AI',
        'subtitle': 'Generative Tools',
        'elements': ['Text to Image', 'AI Fill', 'Auto Edit']
    },

    # Amazon
    'AMZN_aws_growth_1.jpg': {
        'symbol': 'AMZN',
        'icon': '☁️',
        'title': 'AWS',
        'subtitle': 'Cloud Infrastructure',
        'elements': ['EC2', 'S3', 'Lambda']
    },
    'AMZN_ai_platform_2.jpg': {
        'symbol': 'AMZN',
        'icon': '🤖',
        'title': 'AI Services',
        'subtitle': 'Bedrock Platform',
        'elements': ['Multi-Model', 'Scaling', 'Integration']
    },

    # Google
    'GOOGL_search_ai_1.jpg': {
        'symbol': 'GOOGL',
        'icon': '🔍',
        'title': 'AI Search',
        'subtitle': 'Search Evolution',
        'elements': ['Gemini', 'Context', 'Answers']
    },
    'GOOGL_ad_business_2.jpg': {
        'symbol': 'GOOGL',
        'icon': '📊',
        'title': 'Digital Ads',
        'subtitle': 'Advertising Platform',
        'elements': ['Targeting', 'Analytics', 'ROI']
    },

    # Meta
    'META_llama_opensource_1.jpg': {
        'symbol': 'META',
        'icon': '🦙',
        'title': 'Llama AI',
        'subtitle': 'Open Source Model',
        'elements': ['Training', 'Open', 'Community']
    },
    'META_business_tools_2.jpg': {
        'symbol': 'META',
        'icon': '💼',
        'title': 'Business Tools',
        'subtitle': 'Social Commerce',
        'elements': ['Ads', 'Shops', 'Automation']
    },

    # Microsoft
    'MSFT_copilot_integration_1.jpg': {
        'symbol': 'MSFT',
        'icon': '🤝',
        'title': 'Copilot',
        'subtitle': 'AI Assistant',
        'elements': ['Office 365', 'Productivity', 'AI']
    },
    'MSFT_revenue_growth_2.jpg': {
        'symbol': 'MSFT',
        'icon': '📈',
        'title': 'Revenue',
        'subtitle': 'Growth Trajectory',
        'elements': ['Cloud', 'Enterprise', 'Gaming']
    },

    # Netflix
    'NFLX_streaming_content_1.jpg': {
        'symbol': 'NFLX',
        'icon': '🎬',
        'title': 'Streaming',
        'subtitle': 'Content Library',
        'elements': ['Originals', 'Licensed', 'Global']
    },
    'NFLX_advertising_2.jpg': {
        'symbol': 'NFLX',
        'icon': '📺',
        'title': 'Ad Platform',
        'subtitle': 'New Revenue',
        'elements': ['Ad Tier', 'Targeting', 'Growth']
    },

    # NVIDIA
    'NVDA_blackwell_chip_1.jpg': {
        'symbol': 'NVDA',
        'icon': '💎',
        'title': 'Blackwell',
        'subtitle': 'Next-Gen GPU',
        'elements': ['Performance', 'AI Training', 'Power']
    },
    'NVDA_ai_server_tech_2.jpg': {
        'symbol': 'NVDA',
        'icon': '🖥️',
        'title': 'AI Servers',
        'subtitle': 'Data Center Tech',
        'elements': ['H100', 'Clusters', 'Infrastructure']
    },

    # Tesla
    'TSLA_robotaxi_autonomous_1.jpg': {
        'symbol': 'TSLA',
        'icon': '🚖',
        'title': 'Robotaxi',
        'subtitle': 'Autonomous Future',
        'elements': ['FSD', 'Network', 'Vision']
    },
    'TSLA_charging_network_2.jpg': {
        'symbol': 'TSLA',
        'icon': '⚡',
        'title': 'Supercharger',
        'subtitle': 'Charging Network',
        'elements': ['Fast Charge', 'Coverage', 'Standard']
    },

    # Uber
    'UBER_rideshare_profit_1.jpg': {
        'symbol': 'UBER',
        'icon': '🚗',
        'title': 'Rideshare',
        'subtitle': 'Profitability',
        'elements': ['Rides', 'Drivers', 'Growth']
    },
    'UBER_eats_delivery_2.jpg': {
        'symbol': 'UBER',
        'icon': '🍔',
        'title': 'Uber Eats',
        'subtitle': 'Delivery Service',
        'elements': ['Food', 'Logistics', 'Revenue']
    },
}


def create_contextual_image(filename, definition, width=1200, height=630):
    """Create a contextual image that illustrates the article content"""

    symbol = definition['symbol']
    colors = COMPANY_COLORS[symbol]

    # Create image with gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Create subtle gradient background
    primary = colors['primary']
    secondary = colors['secondary']

    for y in range(height):
        ratio = y / height
        r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
        g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
        b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    # Add semi-transparent overlay for text readability
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)

    try:
        # Try to load system fonts
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 80)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 50)
        icon_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 150)
        element_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 35)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        icon_font = ImageFont.load_default()
        element_font = ImageFont.load_default()

    # Draw large icon at the top
    icon = definition['icon']
    icon_bbox = draw.textbbox((0, 0), icon, font=icon_font)
    icon_width = icon_bbox[2] - icon_bbox[0]
    icon_x = (width - icon_width) // 2
    draw.text((icon_x, 80), icon, fill=(255, 255, 255, 255), font=icon_font)

    # Draw title
    title = definition['title']
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 280), title, fill=(255, 255, 255), font=title_font)

    # Draw subtitle
    subtitle = definition['subtitle']
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    draw.text((subtitle_x, 380), subtitle, fill=(220, 220, 220), font=subtitle_font)

    # Draw feature elements as badges
    elements = definition['elements']
    total_elements_width = sum(len(e) * 20 + 40 for e in elements) + (len(elements) - 1) * 20
    start_x = (width - total_elements_width) // 2

    for i, element in enumerate(elements):
        element_width = len(element) * 20 + 40
        x = start_x + i * (element_width + 20)
        y = 480

        # Draw rounded rectangle badge
        badge_color = (255, 255, 255, 30)
        draw.rounded_rectangle(
            [(x, y), (x + element_width, y + 60)],
            radius=10,
            fill=badge_color,
            outline=(255, 255, 255, 150),
            width=2
        )

        # Draw element text
        element_bbox = draw.textbbox((0, 0), element, font=element_font)
        element_text_width = element_bbox[2] - element_bbox[0]
        text_x = x + (element_width - element_text_width) // 2
        draw.text((text_x, y + 12), element, fill=(255, 255, 255), font=element_font)

    return img


def main():
    """Generate all contextual images"""
    output_dir = 'public/images'
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {len(IMAGE_DEFINITIONS)} contextual images...")

    for filename, definition in IMAGE_DEFINITIONS.items():
        filepath = os.path.join(output_dir, filename)
        print(f"Creating {filename}...")

        img = create_contextual_image(filename, definition)
        img.save(filepath, 'JPEG', quality=90)
        print(f"  ✓ Saved to {filepath}")

    print(f"\n✓ Successfully generated {len(IMAGE_DEFINITIONS)} contextual images!")
    print(f"  Images saved to: {output_dir}/")


if __name__ == '__main__':
    main()
