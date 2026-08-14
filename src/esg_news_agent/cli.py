"""Command-line interface for ESG news analysis."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path

from .export import write_articles_csv
from .pipeline import analyze_articles
from .sources import fetch_newsapi, load_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze company news for ESG media signals"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="CSV file containing news articles")
    source.add_argument("--newsapi", action="store_true", help="Fetch articles from NewsAPI")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument(
        "--from-date",
        type=date.fromisoformat,
        default=date.today() - timedelta(days=7),
    )
    parser.add_argument("--to-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--duplicate-threshold", type=float, default=0.90)
    parser.add_argument("--include-non-esg", action="store_true")
    parser.add_argument("--output", type=Path, help="Optional article-level CSV output")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    articles = (
        fetch_newsapi(args.company, args.from_date, args.to_date)
        if args.newsapi
        else load_csv(args.input)
    )
    result = analyze_articles(
        articles,
        duplicate_threshold=args.duplicate_threshold,
        include_non_esg=args.include_non_esg,
    )
    if args.output:
        write_articles_csv(result, args.output)
    summary = {
        "company": args.company,
        **{key: result[key] for key in ("counts", "overall", "pillars")},
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
