"""Deterministic conversation replay for offline AI safety audits."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .dry_run import simulate_decisions
from .observability import summarize_decisions


def replay_decisions(
    messages: Iterable[Mapping[str, Any]],
    decisions: Iterable[Mapping[str, Any]],
    min_confidence: float = 0.75,
) -> dict[str, Any]:
    """Pair bounded conversation samples with model decisions without network calls."""
    message_list = list(messages)
    decision_list = list(decisions)
    simulation = simulate_decisions(decision_list, min_confidence)
    observations = []
    for index, decision in enumerate(decision_list):
        message = message_list[index] if index < len(message_list) else {}
        observations.append({
            "index": index,
            "sender": str(message.get("sender") or ""),
            "message": str(message.get("message") or "")[:500],
            "allowed": bool(decision.get("allowed")),
            "reason": str(decision.get("reason") or ""),
        })
    return {
        "messages": len(message_list),
        "decisions": len(decision_list),
        "simulation": simulation,
        "summary": summarize_decisions(simulation["results"]),
        "observations": observations,
    }
