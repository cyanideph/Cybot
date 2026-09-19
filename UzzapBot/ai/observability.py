"""Small deterministic metrics helpers for AI decision audits."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping


def summarize_decisions(decisions: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    total = 0
    allowed = 0
    reasons = Counter()
    actions = Counter()
    for decision in decisions:
        total += 1
        if bool(decision.get("allowed")):
            allowed += 1
        reasons[str(decision.get("reason") or "unknown")] += 1
        action = str(decision.get("action") or "").strip()
        if action:
            actions[action] += 1
    blocked = total - allowed
    return {
        "total": total,
        "allowed": allowed,
        "blocked": blocked,
        "allow_rate": (allowed / total) if total else 0.0,
        "reasons": dict(sorted(reasons.items())),
        "actions": dict(sorted(actions.items())),
    }
