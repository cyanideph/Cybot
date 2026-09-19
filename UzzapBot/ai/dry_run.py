"""Deterministic simulator for reviewing AI decisions without sending messages."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

from .decision_engine import DecisionEngine


def simulate_decisions(
    decisions: Iterable[Mapping[str, Any]],
    min_confidence: float = 0.75,
) -> dict[str, Any]:
    """Validate a batch of model decisions without network calls or sends."""
    gate = DecisionEngine(min_confidence)
    counts = Counter()
    results = []
    for index, decision in enumerate(decisions):
        checked = gate.validate(dict(decision))
        reason = str(checked.get("reason") or "unknown")
        counts[reason] += 1
        results.append({
            "index": index,
            "allowed": bool(checked.get("allowed")),
            "reason": reason,
            "game": checked.get("game"),
        })
    return {
        "total": len(results),
        "allowed": sum(1 for item in results if item["allowed"]),
        "blocked": sum(1 for item in results if not item["allowed"]),
        "reasons": dict(sorted(counts.items())),
        "results": results,
    }
