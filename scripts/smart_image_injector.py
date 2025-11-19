#!/usr/bin/env python3
"""
Inject image markdown into article sections based on generated metadata.

Inputs:
  - original markdown path
  - images JSON (list of {section_index, image_url, caption, image_type, position})

Outputs:
  - new markdown with inserted image tags (responsive HTML-friendly Markdown).
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


def _build_tag(url: str, alt: str) -> str:
    return f'<picture>\n  <source srcset="{url}" media="(min-width: 720px)">\n  <img src="{url}" alt="{alt}" loading="lazy" style="width:100%;height:auto;border-radius:12px;">\n</picture>'


def inject(markdown_path: Path, images: List[Dict], out_path: Path) -> None:
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    insertions: Dict[int, List[str]] = {}

    for img in images:
        alt = img.get("section_title") or img.get("image_type") or "Blog visual"
        caption = img.get("caption") or f"*{alt}*"
        slot = img.get("image_slot_after_line", len(lines))
        tag = _build_tag(img["image_url"], alt)
        insertions.setdefault(slot, []).append(f"{tag}\n{caption}\n")

    new_lines: List[str] = []
    for idx, line in enumerate(lines, start=1):
        new_lines.append(line)
        if idx in insertions:
            new_lines.extend(insertions[idx])

    if len(lines) + 1 in insertions:
        new_lines.extend(insertions[len(lines) + 1])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"Wrote injected markdown to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Insert generated images into Markdown.")
    parser.add_argument("markdown_path", type=Path)
    parser.add_argument("images_json", type=Path)
    parser.add_argument("--out", type=Path, default=Path("tmp") / "article_with_images.md")
    args = parser.parse_args()

    images = json.loads(args.images_json.read_text(encoding="utf-8"))
    inject(args.markdown_path, images, args.out)


if __name__ == "__main__":
    main()
