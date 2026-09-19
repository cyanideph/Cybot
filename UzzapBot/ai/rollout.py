"""Deterministic production-rollout gate for the UzzapBot AI pipeline.

This module only evaluates rollout readiness. It never enables AI, calls a
network service, writes to Supabase, sends messages, or changes configuration.
""" 
from __future__ import annotations

from typing import Any, Mapping

from ai.security import validate_ai_security_config

STAGES = ("disabled", "dry_run", "canary", "live")


def evaluate_rollout(config: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic rollout decision with safe defaults."""
    security = validate_ai_security_config(config)
    requested_stage = str(config.get("rollout_stage", "disabled")).strip().lower()

    findings = list(security["findings"])
    if requested_stage not in STAGES:
        findings.append("invalid_rollout_stage")
        requested_stage = "disabled"

    if requested_stage in {"canary", "live"}:
        if not security["safe"]:
            findings.append("security_gate_failed")
        if not bool(config.get("ai_enabled")):
            findings.append("global_ai_enable_required")
        if requested_stage == "live" and not bool(config.get("ai_live_enabled")):
            findings.append("live_enable_required")
        if bool(config.get("ai_dry_run")):
            findings.append("dry_run_must_be_disabled")

    if requested_stage == "canary":
        canary_percent = int(config.get("canary_percent", 1))
        if not 1 <= canary_percent <= 10:
            findings.append("invalid_canary_percent")
    else:
        canary_percent = 0

    # Phase 11 never turns a requested stage into an active runtime switch.
    live_path_open = bool(security["live_path_open"])
    return {
        "ready": not findings,
        "requested_stage": requested_stage,
        "canary_percent": canary_percent,
        "findings": findings,
        "runtime_activation": False,
        "network_calls": False,
        "supabase_writes": False,
        "message_sending": False,
        "automatic_tuning": False,
        "rollback_stage": "disabled",
        "live_path_open": live_path_open,
    }


def rollback_plan() -> dict[str, str]:
    """Describe the deterministic emergency rollback target."""
    return {
        "target_stage": "disabled",
        "action": "set rollout_stage=disabled and restart the bot",
        "preserve_data": "do not delete Supabase data",
    }
