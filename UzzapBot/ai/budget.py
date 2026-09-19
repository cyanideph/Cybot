"""Deterministic AI budget gates used before optional model work."""
from __future__ import annotations

from typing import Mapping


def request_budget_available(usage: Mapping[str, int], max_requests_per_day: int) -> bool:
    return int(usage.get("requests_day", 0)) < int(max_requests_per_day)


def response_budget_available(
    usage: Mapping[str, int],
    max_messages_per_hour: int,
    max_messages_per_day: int,
) -> bool:
    return (
        int(usage.get("messages_hour", 0)) < int(max_messages_per_hour)
        and int(usage.get("messages_day", 0)) < int(max_messages_per_day)
    )
