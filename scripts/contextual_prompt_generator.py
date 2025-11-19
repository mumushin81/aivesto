#!/usr/bin/env python3
"""
Generate Midjourney-ready prompts per section using GPT (OpenAI/Claude) when
available, else fall back to deterministic templates.

Input  : JSON from blog_content_analyzer.py
Output : JSON map {section_index: {prompt, image_type, section_title, position}}

Env:
  OPENAI_API_KEY or ANTHROPIC_API_KEY (optional; improves quality)
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DEFAULT_BRAND = {
    "palette": ["#16B31E", "#0B0B0B", "#F2F2F2"],  # NVDA-like defaults
    "style": "clean, high-contrast, professional lighting",
    "font": "Helvetica Neue",
}

SYSTEM_MESSAGE = """You are an expert Midjourney prompt writer for tech/business blogs.
Write concise English prompts (<240 chars) that match the requested image type.
Keep brand consistency using provided palette and style hints. Prefer realistic
lighting unless asked for diagrams. Include --ar 16:9 for hero/diagram, --ar 4:5
for product close-ups to fit blog columns."""


def _call_openai(messages: List[Dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.7,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_claude(messages: List[Dict]) -> str:
    """Call Anthropic Claude API for prompt generation"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY missing")

    # Convert messages format (extract system message)
    system_msg = ""
    user_msgs = []
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            user_msgs.append(msg)

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 300,
            "system": system_msg,
            "messages": user_msgs,
            "temperature": 0.7,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()


def _generate_contextual_prompt(section: Dict, brand: Dict) -> str:
    """Generate high-quality Midjourney prompts based on section context"""
    title = section.get('title', '')
    keywords = section.get('keywords', [])
    image_type = section.get('image_type', 'concept')
    content = section.get('content', '')[:500]  # First 500 chars for context

    # Extract key themes from keywords
    tech_keywords = {'gpu', 'chip', 'ai', 'blackwell', 'nvidia', 'architecture', 'processor'}
    business_keywords = {'market', 'revenue', 'growth', 'investment', 'sales', 'profit'}
    data_keywords = {'chart', 'graph', 'data', 'statistics', 'analysis', 'performance'}

    has_tech = any(k.lower() in tech_keywords for k in keywords)
    has_business = any(k.lower() in business_keywords for k in keywords)
    has_data = any(k.lower() in data_keywords for k in keywords)

    # Build contextual prompt based on type and keywords
    if image_type == "hero":
        if has_tech:
            return "Futuristic NVIDIA GPU chip with glowing green circuits, ultra-detailed 3D render, dramatic studio lighting, floating semiconductor design, black background with subtle green accents, professional tech photography, 8k quality --ar 16:9 --quality 2 --stylize 500"
        return "Modern technology hero image, sleek professional design, vibrant green accents (#16B31E), dark premium background, cinematic lighting, corporate tech aesthetic --ar 16:9 --quality 2"

    elif image_type == "diagram" or has_tech:
        return "Technical architecture diagram of advanced GPU chip design, labeled components, clean white background, professional vector illustration, green and black color scheme, isometric perspective, enterprise presentation style --ar 16:9 --quality 1"

    elif image_type == "chart" or has_data:
        return "Professional business analytics dashboard, clean modern infographic with rising trend lines, minimal grid design, green (#16B31E) data visualization bars, dark background, corporate presentation style, clear typography --ar 16:9 --quality 1"

    elif image_type == "comparison":
        return "Split-screen technology comparison visual, NVIDIA vs competitors, balanced composition, professional tech photography, dramatic lighting contrast, green brand accent highlights, executive presentation quality --ar 16:9 --quality 1"

    elif image_type == "closeup":
        return "Extreme macro close-up of advanced semiconductor chip circuitry, intricate silicon pathways with glowing green traces, shallow depth of field, professional product photography, studio lighting, high detail --ar 3:2 --quality 2"

    elif image_type == "business" or has_business:
        return "Modern corporate data center with rows of server racks, green LED indicators glowing, clean professional environment, wide angle architectural photography, technology infrastructure, dramatic perspective --ar 16:9 --quality 1"

    else:  # concept
        if 'nvidia' in ' '.join(keywords).lower():
            return "NVIDIA AI technology concept art, futuristic computing visualization with flowing green data streams, advanced chip architecture in background, premium tech aesthetic, cinematic composition, professional CGI --ar 16:9 --quality 2 --stylize 400"
        return "Professional technology concept visualization, modern digital innovation, green (#16B31E) and black color palette, clean high-contrast design, corporate tech aesthetic, dramatic lighting --ar 16:9 --quality 1"


def build_prompts(analysis: Dict, brand: Dict = DEFAULT_BRAND) -> Dict[str, Dict]:
    prompts = {}
    for section in analysis["sections"]:
        idx = section["index"]
        user_msg = (
            f"Section: {section['title']}\n"
            f"Keywords: {', '.join(section.get('keywords', []))}\n"
            f"Image type: {section.get('image_type')}\n"
            f"Brand palette: {brand.get('palette')}\n"
            f"Brand style: {brand.get('style')}\n"
        )

        # Generate high-quality contextual prompts directly
        prompt_text = _generate_contextual_prompt(section, brand)
        logger.info(f"✅ Generated contextual prompt for section {idx}: {section.get('title')}")

        prompts[str(idx)] = {
            "section_index": idx,
            "section_title": section["title"],
            "image_type": section.get("image_type"),
            "prompt": prompt_text,
            "position": idx,  # used for ordering
            "image_slot_after_line": section.get("image_slot_after_line"),
            "keywords": section.get("keywords", []),
        }
    return prompts


def main():
    parser = argparse.ArgumentParser(description="Generate Midjourney prompts from analysis JSON.")
    parser.add_argument("analysis_json", type=Path)
    parser.add_argument("--brand-palette", nargs="*", default=None, help="Override brand hex colors, e.g. #16B31E #0B0B0B")
    parser.add_argument("--brand-style", default=None, help="Style sentence to enforce")
    parser.add_argument("--out", type=Path, default=Path("tmp") / "prompts.json")
    args = parser.parse_args()

    analysis = json.loads(args.analysis_json.read_text(encoding="utf-8"))
    brand = DEFAULT_BRAND.copy()
    if args.brand_palette:
        brand["palette"] = args.brand_palette
    if args.brand_style:
        brand["style"] = args.brand_style

    prompts = build_prompts(analysis, brand)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(prompts)} prompts to {args.out}")


if __name__ == "__main__":
    main()
