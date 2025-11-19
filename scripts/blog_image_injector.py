"""Lightweight HTML injector to add hero images into public/blog.html cards."""
import json
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup
from loguru import logger


class BlogImageInjector:
    def __init__(self, blog_html: Path):
        self.blog_html = Path(blog_html)
        if not self.blog_html.exists():
            raise FileNotFoundError(f"blog HTML not found: {blog_html}")

    def load_cards(self) -> BeautifulSoup:
        html = self.blog_html.read_text(encoding="utf-8")
        return BeautifulSoup(html, "html.parser")

    def save_cards(self, soup: BeautifulSoup):
        self.blog_html.write_text(str(soup), encoding="utf-8")

    def inject_cards(self, cards: List[Dict]):
        """
        cards: [{symbol, title, date, url, image_url, topic}]
        New cards are prepended to .articles-grid preserving existing cards.
        """
        soup = self.load_cards()
        grid = soup.find("div", {"class": "articles-grid"})
        if not grid:
            raise RuntimeError(".articles-grid not found in blog.html")

        for card in cards[::-1]:  # reverse so first in list ends up first visually
            card_div = soup.new_tag("div", **{"class": "article-card"})
            card_div["onclick"] = f"location.href='{card['url']}'"

            header = soup.new_tag("div", **{"class": "article-header"})
            symbol_span = soup.new_tag("span", **{"class": "symbol-tag"})
            symbol_span.string = card.get("symbol", "-")
            date_div = soup.new_tag("div", **{"class": "article-date"})
            date_div.string = f"📅 {card.get('date','')}"

            header.append(symbol_span)
            header.append(date_div)
            card_div.append(header)

            title = soup.new_tag("h2", **{"class": "article-title"})
            title.string = card.get("title", card.get("topic", "New Image"))
            card_div.append(title)

            img = soup.new_tag("img", **{"class": "article-image", "src": card.get("image_url", ""), "alt": card.get("topic", "")})
            card_div.insert(0, img)

            read_more = soup.new_tag("span", **{"class": "read-more"})
            read_more.string = "자세히 보기 →"
            card_div.append(read_more)

            grid.insert(0, card_div)

        self.save_cards(soup)
        logger.info(f"Injected {len(cards)} card(s) into {self.blog_html}")


def build_card(article_id: str, image_url: str, symbol: str, topic: str, date: str) -> Dict:
    return {
        "symbol": symbol,
        "title": topic,
        "date": date,
        "url": f"/articles/{article_id}.html",
        "image_url": image_url,
        "topic": topic,
    }


__all__ = ["BlogImageInjector", "build_card"]
