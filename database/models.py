from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class PriceImpact(Enum):
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"

class Importance(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class RawNews:
    """원본 뉴스 데이터 모델"""
    source: str
    title: str
    url: str
    content: Optional[str]
    published_at: datetime
    symbols: List[str]
    metadata: Dict
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "published_at": self.published_at.isoformat(),
            "symbols": self.symbols,
            "metadata": self.metadata
        }

@dataclass
class AnalyzedNews:
    """분석된 뉴스 데이터 모델"""
    raw_news_id: str
    relevance_score: int
    affected_symbols: List[str]
    price_impact: PriceImpact
    importance: Importance
    analysis: Dict
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "raw_news_id": self.raw_news_id,
            "relevance_score": self.relevance_score,
            "affected_symbols": self.affected_symbols,
            "price_impact": self.price_impact.value,
            "importance": self.importance.value,
            "analysis": self.analysis
        }

@dataclass
class PublishedArticle:
    """발행된 블로그 글 모델"""
    title: str
    content: str
    analyzed_news_ids: List[str]
    wordpress_id: Optional[int] = None
    published_at: Optional[datetime] = None
    views: int = 0
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "analyzed_news_ids": self.analyzed_news_ids,
            "wordpress_id": self.wordpress_id,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "views": self.views
        }
