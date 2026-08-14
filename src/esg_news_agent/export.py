"""Result export helpers."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any


def articles_to_csv(result: dict[str, Any]) -> str:
    rows = result.get("articles", [])
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def write_articles_csv(result: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(articles_to_csv(result), encoding="utf-8")
