"""Input adapters for CSV files and NewsAPI."""

from __future__ import annotations

import csv
from datetime import date
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Article

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"
ESG_QUERY = (
    '(ESG OR sustainability OR climate OR emissions OR employees OR '
    '"human rights" OR governance OR compliance)'
)


def load_csv(path: str | Path) -> list[Article]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "title" not in reader.fieldnames:
            raise ValueError("CSV input must contain a 'title' column")
        return [
            Article(
                title=(row.get("title") or "").strip(),
                description=(row.get("description") or "").strip(),
                url=(row.get("url") or "").strip(),
                source=(row.get("source") or "").strip(),
                published_at=(row.get("published_at") or "").strip(),
            )
            for row in reader
            if (row.get("title") or "").strip()
        ]


def fetch_newsapi(
    company: str,
    from_date: date,
    to_date: date,
    *,
    api_key: str | None = None,
    page_size: int = 100,
) -> list[Article]:
    """Fetch English ESG-related company coverage from NewsAPI."""
    key = api_key or os.getenv("NEWS_API_KEY")
    if not key:
        raise ValueError("Set NEWS_API_KEY before using NewsAPI")
    if from_date > to_date:
        raise ValueError("from_date must not be after to_date")

    params = {
        "q": f'"{company.strip()}" AND {ESG_QUERY}',
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(max(page_size, 1), 100),
        "apiKey": key,
    }
    request = Request(
        f"{NEWSAPI_ENDPOINT}?{urlencode(params)}",
        headers={"User-Agent": "esg-news-intelligence-agent/0.1"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"NewsAPI returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach NewsAPI: {exc.reason}") from exc

    if payload.get("status") != "ok":
        raise RuntimeError(payload.get("message", "NewsAPI request failed"))

    return [
        Article(
            title=(item.get("title") or "").strip(),
            description=(item.get("description") or "").strip(),
            url=(item.get("url") or "").strip(),
            source=((item.get("source") or {}).get("name") or "").strip(),
            published_at=(item.get("publishedAt") or "").strip(),
        )
        for item in payload.get("articles", [])
        if (item.get("title") or "").strip()
    ]
