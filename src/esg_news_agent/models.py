"""Data models shared by the ESG analysis pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Article:
    title: str
    description: str = ""
    url: str = ""
    source: str = ""
    published_at: str = ""

    @property
    def text(self) -> str:
        return " ".join(part.strip() for part in (self.title, self.description) if part.strip())


@dataclass(frozen=True)
class ArticleAnalysis:
    article: Article
    pillars: tuple[str, ...]
    primary_pillar: str
    keyword_hits: dict[str, tuple[str, ...]] = field(default_factory=dict)
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self.article)
        row.update(
            {
                "pillars": ",".join(self.pillars),
                "primary_pillar": self.primary_pillar,
                "keyword_hits": "; ".join(
                    f"{pillar}: {', '.join(words)}"
                    for pillar, words in self.keyword_hits.items()
                    if words
                ),
                "sentiment_score": self.sentiment_score,
                "sentiment_label": self.sentiment_label,
            }
        )
        return row
