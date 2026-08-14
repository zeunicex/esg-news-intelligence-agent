"""Text similarity and sentiment helpers with no external dependencies."""

from __future__ import annotations

from collections import Counter
import math
import re

from .models import Article

TOKEN_PATTERN = re.compile(r"[a-z][a-z'-]+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "their", "this", "to", "was", "were", "will", "with",
}
POSITIVE_WORDS = {
    "accountable", "award", "clean", "compliant", "diverse", "efficient",
    "ethical", "improve", "improved", "improves", "innovation", "leader",
    "progress", "protect", "reduced", "renewable", "responsible", "safe",
    "strong", "sustainable", "transparent", "upgrade",
}
NEGATIVE_WORDS = {
    "abuse", "accident", "bribery", "breach", "corruption", "criticized",
    "deforestation", "discrimination", "emission", "emissions", "excessive",
    "exploit", "fine", "fines", "fraud", "greenwashing", "harassment", "injury",
    "lawsuit", "leak", "misconduct", "pollution", "recall", "risk", "risks",
    "unsafe", "violation", "waste", "weak",
}
NEGATIONS = {"no", "not", "never", "neither", "without"}


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOP_WORDS]


def sentiment(text: str) -> tuple[float, str]:
    """Return a transparent lexicon score in [-1, 1] and a label."""
    tokens = tokenize(text)
    raw_score = 0.0
    for index, token in enumerate(tokens):
        value = float(token in POSITIVE_WORDS) - float(token in NEGATIVE_WORDS)
        if value and any(word in NEGATIONS for word in tokens[max(0, index - 3):index]):
            value *= -1
        raw_score += value

    score = math.tanh(raw_score / 3.0)
    label = "positive" if score >= 0.20 else "negative" if score <= -0.20 else "neutral"
    return round(score, 4), label


def _tfidf_vectors(texts: list[str]) -> list[dict[str, float]]:
    documents = [Counter(tokenize(text)) for text in texts]
    document_frequency = Counter(token for doc in documents for token in doc)
    total_documents = max(len(documents), 1)
    vectors: list[dict[str, float]] = []

    for document in documents:
        total_terms = sum(document.values()) or 1
        vector = {
            token: (count / total_terms)
            * (math.log((1 + total_documents) / (1 + document_frequency[token])) + 1)
            for token, count in document.items()
        }
        vectors.append(vector)
    return vectors


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    common = left.keys() & right.keys()
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def deduplicate_articles(
    articles: list[Article],
    threshold: float = 0.90,
) -> tuple[list[Article], int]:
    """Keep the first article in each near-duplicate cluster."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("duplicate threshold must be between 0 and 1")
    vectors = _tfidf_vectors([article.text for article in articles])
    kept_indices: list[int] = []
    for index, vector in enumerate(vectors):
        if all(cosine_similarity(vector, vectors[kept]) < threshold for kept in kept_indices):
            kept_indices.append(index)
    return [articles[index] for index in kept_indices], len(articles) - len(kept_indices)
