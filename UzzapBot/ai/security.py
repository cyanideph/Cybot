"""Deterministic security policy for the UzzapBot AI pipeline.

This module validates configuration and model output metadata without making
network calls or changing runtime configuration.
"""
from __future__ import annotations

from typing import Any, Mapping


def validate_ai_security_config(config: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[str] = []

    if bool(config.get("ai_live_enabled")) and bool(config.get("ai_dry_run")):
        findings.append("conflicting_live_and_dry_run")

    if bool(config.get("ai_live_enabled")) and not bool(config.get("ai_enabled")):
        findings.append("live_enabled_without_ai_enabled")

    try:
        min_confidence = float(config.get("min_confidence", 0.75))
    except (TypeError, ValueError):
        findings.append("invalid_min_confidence")
        min_confidence = 0.0

    if not 0.0 < min_confidence <= 1.0:
        if "invalid_min_confidence" not in findings:
            findings.append("invalid_min_confidence")

    try:
        max_messages_per_hour = int(config.get("max_messages_per_hour", 3))
        max_messages_per_day = int(config.get("max_messages_per_day", 20))
        max_requests_per_day = int(config.get("max_requests_per_day", 100))
    except (TypeError, ValueError):
        findings.append("invalid_budget")
        max_messages_per_hour = max_messages_per_day = max_requests_per_day = 0

    if max_messages_per_hour < 0 or max_messages_per_day < 0 or max_requests_per_day < 0:
        findings.append("negative_budget")

    return {
        "safe": not findings,
        "findings": findings,
        "live_path_open": bool(
            config.get("ai_enabled")
            and config.get("ai_live_enabled")
            and not config.get("ai_dry_run")
        ),
        "min_confidence": min_confidence,
        "budgets": {
            "messages_per_hour": max_messages_per_hour,
            "messages_per_day": max_messages_per_day,
            "requests_per_day": max_requests_per_day,
        },
        "network_calls": False,
        "supabase_writes": False,
        "automatic_tuning": False,
    }


def sanitize_ai_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Return non-secret audit metadata only."""
    allowed = {
        "room",
        "action",
        "topic",
        "reason",
        "confidence",
        "model",
        "dry_run",
    }
    return {key: metadata[key] for key in allowed if key in metadata}
