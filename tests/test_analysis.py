import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from esg_news_agent.models import Article
from esg_news_agent.pipeline import analyze_articles
from esg_news_agent.sources import load_csv
from esg_news_agent.taxonomy import classify_esg
from esg_news_agent.text import deduplicate_articles, sentiment


class ESGAnalysisTests(unittest.TestCase):
    def test_classifier_can_return_multiple_pillars(self):
        pillars, hits = classify_esg(
            "The board approved worker safety and renewable energy targets."
        )
        self.assertEqual(
            set(pillars),
            {"Environmental", "Social", "Governance"},
        )
        self.assertIn("renewable", hits["Environmental"])

    def test_sentiment_separates_positive_and_negative_language(self):
        positive, positive_label = sentiment(
            "Improved safe renewable and transparent program"
        )
        negative, negative_label = sentiment(
            "Fraud bribery pollution violation"
        )
        self.assertGreater(positive, 0)
        self.assertEqual(positive_label, "positive")
        self.assertLess(negative, 0)
        self.assertEqual(negative_label, "negative")

    def test_near_duplicates_are_removed(self):
        articles = [
            Article(
                "Company opens renewable energy facility",
                "Clean energy will reduce emissions",
            ),
            Article(
                "Company opens renewable energy facility",
                "Clean energy will reduce emissions",
            ),
            Article(
                "Board starts a compliance audit",
                "Governance review begins",
            ),
        ]
        unique, removed = deduplicate_articles(articles)
        self.assertEqual(len(unique), 2)
        self.assertEqual(removed, 1)

    def test_sample_pipeline_is_reproducible(self):
        result = analyze_articles(
            load_csv(ROOT / "examples" / "sample_news.csv")
        )
        self.assertEqual(result["counts"]["collected"], 10)
        self.assertEqual(result["counts"]["duplicates_removed"], 1)
        self.assertEqual(result["counts"]["esg_relevant"], 8)
        self.assertGreater(
            result["pillars"]["Environmental"]["article_count"],
            0,
        )
        self.assertGreater(
            result["pillars"]["Social"]["article_count"],
            0,
        )
        self.assertGreater(
            result["pillars"]["Governance"]["article_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
