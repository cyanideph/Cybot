"""Deterministic feedback signals for offline AI decision evaluation."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping


def evaluate_feedback(
    decisions: Iterable[Mapping[str, Any]],
    *,
    min_confidence: float = 0.75,
    max_block_rate: float = 0.50,
) -> dict[str, Any]:
    """Summarize decision quality without calling AI or mutating state."""
    items = list(decisions)
    total = len(items)
    allowed = sum(1 for item in items if bool(item.get("allowed")))
    blocked = total - allowed
    reasons = Counter(str(item.get("reason") or "unknown") for item in items)
    low_confidence = reasons.get("low_confidence", 0)
    block_rate = (blocked / total) if total else 0.0
    confidence_values = []
    for item in items:
        try:
            value = float(item.get("confidence"))
        except (TypeError, ValueError):
            continue
        if 0.0 <= value <= 1.0:
            confidence_values.append(value)
    mean_confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values else 0.0
    )
    return {
        "total": total,
        "allowed": allowed,
        "blocked": blocked,
        "block_rate": block_rate,
        "mean_confidence": mean_confidence,
        "low_confidence": low_confidence,
        "feedback": (
            "insufficient_data" if not total
            else "review" if block_rate > max_block_rate
            else "healthy"
        ),
        "min_confidence": min_confidence,
        "max_block_rate": max_block_rate,
    }
