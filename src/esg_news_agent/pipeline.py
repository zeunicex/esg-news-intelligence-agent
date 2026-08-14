"""End-to-end ESG news analysis pipeline."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .models import Article, ArticleAnalysis
from .taxonomy import classify_esg, primary_pillar
from .text import deduplicate_articles, sentiment

PILLARS = ("Environmental", "Social", "Governance")


def _coerce_articles(records: Iterable[Article | dict[str, Any]]) -> list[Article]:
    articles: list[Article] = []
    for record in records:
        if isinstance(record, Article):
            articles.append(record)
        else:
            articles.append(
                Article(
                    title=str(record.get("title", "")).strip(),
                    description=str(record.get("description", "")).strip(),
                    url=str(record.get("url", "")).strip(),
                    source=str(record.get("source", "")).strip(),
                    published_at=str(record.get("published_at", "")).strip(),
                )
            )
    return [article for article in articles if article.title]


def _summary(
    analyses: list[ArticleAnalysis],
    pillar: str | None = None,
) -> dict[str, Any]:
    selected = [item for item in analyses if pillar is None or pillar in item.pillars]
    counts = Counter(item.sentiment_label for item in selected)
    average = sum(item.sentiment_score for item in selected) / len(selected) if selected else 0.0
    return {
        "article_count": len(selected),
        "positive": counts["positive"],
        "neutral": counts["neutral"],
        "negative": counts["negative"],
        "average_sentiment": round(average, 4),
        "media_signal_score": round(50.0 + 50.0 * average, 1),
    }


def analyze_articles(
    records: Iterable[Article | dict[str, Any]],
    *,
    duplicate_threshold: float = 0.90,
    include_non_esg: bool = False,
) -> dict[str, Any]:
    """Deduplicate, classify, score, and summarize article records."""
    collected = _coerce_articles(records)
    unique_articles, duplicates_removed = deduplicate_articles(
        collected,
        duplicate_threshold,
    )
    analyses: list[ArticleAnalysis] = []

    for article in unique_articles:
        pillars, hits = classify_esg(article.text)
        if not pillars and not include_non_esg:
            continue
        score, label = sentiment(article.text)
        analyses.append(
            ArticleAnalysis(
                article=article,
                pillars=pillars,
                primary_pillar=primary_pillar(hits),
                keyword_hits=hits,
                sentiment_score=score,
                sentiment_label=label,
            )
        )

    return {
        "methodology": {
            "classification": "transparent ESG keyword taxonomy",
            "deduplication": "TF-IDF cosine similarity",
            "duplicate_threshold": duplicate_threshold,
            "sentiment": "lightweight contextual lexicon",
            "score_note": "Media signal only; not a standardized ESG rating.",
        },
        "counts": {
            "collected": len(collected),
            "after_deduplication": len(unique_articles),
            "duplicates_removed": duplicates_removed,
            "esg_relevant": sum(bool(item.pillars) for item in analyses),
        },
        "overall": _summary(analyses),
        "pillars": {pillar: _summary(analyses, pillar) for pillar in PILLARS},
        "articles": [item.to_dict() for item in analyses],
    }
