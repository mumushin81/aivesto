#!/usr/bin/env python3
"""
Generate high-quality contextual images programmatically
Creates clean, professional gradient images based on article context
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from typing import Dict
from loguru import logger


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_diagonal_gradient(width: int, height: int, color1: str, color2: str, direction: str = 'tl-br') -> Image.Image:
    """Create smooth diagonal gradient"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    for y in range(height):
        for x in range(width):
            if direction == 'tl-br':
                ratio = (x + y) / (width + height)
            elif direction == 'tr-bl':
                ratio = ((width - x) + y) / (width + height)
            else:
                ratio = (x + (height - y)) / (width + height)

            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)

            draw.point((x, y), fill=(r, g, b))

    return img


def create_tech_gradient(width: int = 1600, height: int = 900, theme: str = "nvidia") -> Image.Image:
    """Create professional tech gradient based on theme"""
    themes = {
        "nvidia": ("#0B0B0B", "#16B31E", "tl-br"),
        "tech_blue": ("#0A1929", "#1E88E5", "tr-bl"),
        "premium": ("#1A1A1A", "#4A4A4A", "tl-br"),
        "vibrant": ("#16B31E", "#0B0B0B", "bl-tr"),
    }

    color1, color2, direction = themes.get(theme, themes["nvidia"])
    return create_diagonal_gradient(width, height, color1, color2, direction)


def generate_image_for_section(section: Dict, output_path: Path, theme: str = "nvidia") -> str:
    """Generate contextual image for a blog section"""
    image_type = section.get('image_type', 'concept')
    keywords = section.get('keywords', [])

    if image_type == 'hero' or any('nvidia' in k.lower() for k in keywords):
        img = create_tech_gradient(1600, 900, "nvidia")
    elif image_type == 'diagram' or any(k.lower() in ['gpu', 'chip', 'architecture'] for k in keywords):
        img = create_tech_gradient(1600, 900, "tech_blue")
    elif image_type == 'business' or any(k.lower() in ['market', 'revenue', 'growth'] for k in keywords):
        img = create_tech_gradient(1600, 900, "premium")
    else:
        img = create_tech_gradient(1600, 900, "vibrant")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'JPEG', quality=95, optimize=True)
    logger.info(f"✅ Generated image: {output_path}")
    return str(output_path)


def generate_all_images(prompts_json: Path, output_dir: Path) -> Dict:
    """Generate all images from prompts JSON"""
    prompts = json.loads(prompts_json.read_text(encoding='utf-8'))
    results = {}

    for idx, (key, prompt_data) in enumerate(prompts.items()):
        section_title = prompt_data.get('section_title', f'section_{idx}')
        safe_title = "".join(c for c in section_title if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        output_file = output_dir / f"image_{idx}_{safe_title}.jpg"
        image_path = generate_image_for_section(prompt_data, output_file)

        results[key] = {
            **prompt_data,
            'local_path': image_path,
            'generated': True,
        }

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate contextual images")
    parser.add_argument("prompts_json", type=Path, help="Prompts JSON file")
    parser.add_argument("--output-dir", type=Path, default=Path("tmp/generated_images"))
    parser.add_argument("--out", type=Path, default=Path("tmp/images.json"))
    args = parser.parse_args()

    results = generate_all_images(args.prompts_json, args.output_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.success(f"✅ Generated {len(results)} images → {args.out}")
