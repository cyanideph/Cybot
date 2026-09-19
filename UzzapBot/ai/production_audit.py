"""Deterministic production-readiness audit for the AI pipeline.

This module is intentionally offline-only. It analyzes recorded decision data
and configuration snapshots; it never calls AI, writes to Supabase, sends
messages, or changes runtime configuration.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .feedback import evaluate_feedback
from .observability import summarize_decisions


def build_production_audit(
    decisions: Iterable[Mapping[str, Any]],
    *,
    ai_enabled: bool,
    ai_dry_run: bool,
    ai_live_enabled: bool,
    room_opt_in_count: int = 0,
    min_confidence: float = 0.75,
) -> dict[str, Any]:
    """Build a deterministic audit report from recorded decisions and config."""
    decision_list = list(decisions)
    summary = summarize_decisions(decision_list)
    feedback = evaluate_feedback(
        decision_list,
        min_confidence=min_confidence,
    )

    live_path_open = bool(ai_enabled and not ai_dry_run and ai_live_enabled)
    safety_findings: list[str] = []
    if live_path_open:
        safety_findings.append("live_ai_path_enabled")
    if room_opt_in_count < 0:
        safety_findings.append("invalid_room_opt_in_count")
    if not 0.0 < min_confidence <= 1.0:
        safety_findings.append("invalid_min_confidence")

    return {
        "status": "review" if safety_findings else "ready_for_controlled_rollout",
        "runtime": {
            "ai_enabled": bool(ai_enabled),
            "ai_dry_run": bool(ai_dry_run),
            "ai_live_enabled": bool(ai_live_enabled),
            "room_opt_in_count": int(room_opt_in_count),
            "live_path_open": live_path_open,
        },
        "summary": summary,
        "feedback": feedback,
        "safety_findings": safety_findings,
        "automatic_tuning": False,
        "network_calls": False,
        "supabase_writes": False,
        "message_sending": False,
    }
