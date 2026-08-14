# ESG News Intelligence Agent

A lightweight, reproducible version of the ESG component described in the
ISY 5005 Investor Intelligence Agent report. It collects company news,
removes near-duplicates, classifies ESG topics, scores article sentiment, and
summarizes Environmental, Social, and Governance media signals.

> The scores in this project are news-based indicators for research and
> education. They are not standardized ESG ratings or investment advice.

## What is included

- NewsAPI collection with credentials loaded from the environment
- CSV input for offline and reproducible analysis
- TF-IDF and cosine-similarity duplicate filtering
- Transparent Environmental, Social, and Governance taxonomy
- Lightweight sentiment analysis with pillar and overall summaries
- Streamlit dashboard and CSV download
- Runnable analysis notebook, synthetic sample data, and unit tests

## Quick start

Python 3.9 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
esg-news --input examples/sample_news.csv --company "Northstar Industries"
```

The command prints a JSON summary. Add `--output results.csv` to export the
article-level analysis.

## Use NewsAPI

Create a key at [NewsAPI](https://newsapi.org/), then set it locally. Never
commit the real key.

```bash
export NEWS_API_KEY="your-key"
esg-news --newsapi --company "Apple" --from-date 2026-08-01 --to-date 2026-08-14
```

NewsAPI plan limits and historical-access rules still apply.

## Dashboard

```bash
pip install -e '.[app]'
streamlit run streamlit_app.py
```

The dashboard can use the included sample data, an uploaded CSV, or NewsAPI.
Uploaded CSV files need a `title` column and may include `description`, `url`,
`source`, and `published_at`.

## Notebook

Open `notebooks/esg_news_analysis.ipynb` from the repository root. It runs on
the synthetic sample file and needs no API key.

## Method

1. Combine each article title and description.
2. Remove near-duplicates using TF-IDF cosine similarity (default: `0.90`).
3. Match transparent ESG terms. An article may map to more than one pillar.
4. Calculate a bounded sentiment score from `-1` to `1`.
5. Convert the average sentiment to a `0` to `100` media-signal score, where
   `50` is neutral.

This baseline is intentionally auditable and light enough to run on a laptop.
The taxonomy and sentiment interface can later be replaced with the report's
proposed EnvRoBERTa, SocialBERT, and GovRoBERTa models after model validation.

## Project structure

```text
src/esg_news_agent/     Core collection and analysis package
streamlit_app.py        Interactive dashboard
examples/               Synthetic offline input
notebooks/              Reproducible walkthrough
tests/                  Standard-library unit tests
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Known limitations

- Keyword classification can miss context, sarcasm, and emerging terminology.
- News sentiment can reflect media coverage rather than company performance.
- Article volume differs by company, geography, language, and source.
- Scores should be validated against disclosures and trusted ESG datasets.

## License

MIT
