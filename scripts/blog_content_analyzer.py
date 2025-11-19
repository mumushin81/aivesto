#!/usr/bin/env python3
"""
Light‑weight Markdown analyzer that extracts section blocks, keywords, and
recommended image slots for downstream Midjourney prompt generation.

Usage:
    python scripts/blog_content_analyzer.py articles/article_NVDA_blackwell_gpu_20251113.md \
        --min-images 5 --out tmp/analysis.json
"""

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional

STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "to", "in", "is", "are", "for", "on",
    "with", "that", "as", "at", "by", "from", "this", "it", "be", "will",
    "can", "not", "we", "our", "their", "has", "have", "had", "but", "if",
    "into", "about", "over", "per", "vs", "vs.", "###", "##", "#",
}


@dataclass
class Section:
    index: int
    title: str
    content: str
    keywords: List[str]
    image_slot_after_line: int
    image_type: str  # hero | diagram | chart | comparison | closeup | concept


def _extract_heading(line: str) -> Optional[str]:
    match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
    if not match:
        return None
    return match.group(2).strip()


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z가-힣0-9]{3,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _guess_image_type(title: str) -> str:
    title_lower = title.lower()
    if "architecture" in title_lower or "구조" in title_lower:
        return "diagram"
    if "시장" in title_lower or "market" in title_lower or "분석" in title_lower:
        return "chart"
    if "경쟁" in title_lower or "대응" in title_lower or "vs" in title_lower:
        return "comparison"
    if "투자" in title_lower or "주가" in title_lower:
        return "business"
    if "기술" in title_lower or "상세" in title_lower or "spec" in title_lower:
        return "closeup"
    return "concept"


def analyze_markdown(path: Path, min_images: int = 5) -> Dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: List[Section] = []

    current_title = lines[0].lstrip("# ").strip() if lines else "Untitled"
    buffer: List[str] = []
    start_line = 0
    section_index = 0

    def flush_section(title: str, content_lines: List[str], start: int, idx: int):
        content = "\n".join(content_lines).strip()
        tokens = _tokenize(content)
        keywords = [w for w, _ in Counter(tokens).most_common(8)]
        image_type = "hero" if idx == 0 else _guess_image_type(title)
        return Section(
            index=idx,
            title=title,
            content=content,
            keywords=keywords,
            image_slot_after_line=start + len(content_lines),
            image_type=image_type,
        )

    for lineno, line in enumerate(lines):
        heading = _extract_heading(line)
        if heading and lineno != 0:  # treat first heading as title
            if buffer:
                sections.append(flush_section(current_title, buffer, start_line, section_index))
                section_index += 1
            current_title = heading
            buffer = []
            start_line = lineno
        else:
            buffer.append(line)

    if buffer:
        sections.append(flush_section(current_title, buffer, start_line, section_index))

    # Ensure minimum image slots by adding concept slots to long sections
    while len(sections) < min_images:
        sections.append(
            Section(
                index=len(sections),
                title=f"Supplemental Visual {len(sections)+1}",
                content="",
                keywords=[],
                image_slot_after_line=len(lines),
                image_type="concept",
            )
        )

    article_title = sections[0].title if sections else path.stem
    return {
        "article_path": str(path),
        "article_title": article_title,
        "sections": [asdict(s) for s in sections],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze a Markdown article for image planning.")
    parser.add_argument("markdown_path", type=Path)
    parser.add_argument("--min-images", type=int, default=5)
    parser.add_argument("--out", type=Path, default=Path("tmp") / "article_analysis.json")
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    analysis = analyze_markdown(args.markdown_path, min_images=args.min_images)
    args.out.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved analysis to {args.out}")


if __name__ == "__main__":
    main()
