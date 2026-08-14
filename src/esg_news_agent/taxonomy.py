"""Transparent ESG topic taxonomy used by the baseline classifier."""

from __future__ import annotations

import re

ESG_TAXONOMY: dict[str, tuple[str, ...]] = {
    "Environmental": (
        "carbon", "climate", "emission", "emissions", "renewable", "clean energy",
        "energy efficiency", "pollution", "waste", "recycling", "water",
        "biodiversity", "deforestation", "environmental regulation",
        "net zero", "greenhouse gas", "circular economy",
    ),
    "Social": (
        "employee", "worker", "workplace", "labor", "human rights",
        "diversity", "diverse", "inclusion", "gender pay", "health and safety",
        "community", "customer safety", "data privacy", "supply chain",
        "accessibility", "training", "union",
    ),
    "Governance": (
        "board", "director", "executive pay", "audit", "shareholder",
        "ethics", "bribery", "corruption", "fraud", "compliance",
        "regulatory", "disclosure", "transparency", "transparent", "whistleblower",
        "antitrust", "tax avoidance", "data governance",
    ),
}


def _contains_term(text: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, flags=re.IGNORECASE))


def classify_esg(text: str) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    """Return all matching ESG pillars and the terms that produced each match."""
    hits = {
        pillar: tuple(term for term in terms if _contains_term(text, term))
        for pillar, terms in ESG_TAXONOMY.items()
    }
    pillars = tuple(pillar for pillar, terms in hits.items() if terms)
    return pillars, hits


def primary_pillar(hits: dict[str, tuple[str, ...]]) -> str:
    """Choose the pillar with the most keyword evidence."""
    non_empty = [(pillar, len(words)) for pillar, words in hits.items() if words]
    if not non_empty:
        return "Non-ESG"
    return max(non_empty, key=lambda item: item[1])[0]
