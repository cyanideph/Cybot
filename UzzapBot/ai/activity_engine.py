"""Deterministic room-activity intelligence for UzzapBot.

Phase 1 deliberately contains no LLM calls. It turns raw human messages into
room state and safe AI eligibility signals. Later AI phases consume these
signals rather than deciding directly from the polling stream.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(UTC)


def parse_timestamp(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


@dataclass
class RoomActivity:
    room_name: str
    enabled: bool = False
    idle_threshold_seconds: int = 900
    inactive_threshold_seconds: int = 3600
    cooldown_seconds: int = 1800
    max_messages_per_hour: int = 3
    max_messages_per_day: int = 20
    last_human_activity_at: datetime | None = None
    last_bot_activity_at: datetime | None = None
    last_ai_analysis_at: datetime | None = None
    activity_state: str = "INACTIVE"
    human_message_count_hour: int = 0
    human_message_count_day: int = 0
    hour_bucket: str = ""
    day_bucket: str = ""

    def refresh(self, now: datetime | None = None) -> str:
        now = now or utcnow()
        last = self.last_human_activity_at
        if last is None:
            self.activity_state = "INACTIVE"
            return self.activity_state

        age = max(0.0, (now - last).total_seconds())
        if age >= self.inactive_threshold_seconds:
            self.activity_state = "INACTIVE"
        elif age >= self.idle_threshold_seconds:
            self.activity_state = "QUIET"
        else:
            self.activity_state = "ACTIVE"
        return self.activity_state

    def record_human_message(self, at: datetime | None = None) -> None:
        at = at or utcnow()
        hour_bucket = at.strftime("%Y-%m-%dT%H")
        day_bucket = at.strftime("%Y-%m-%d")
        if hour_bucket != self.hour_bucket:
            self.hour_bucket = hour_bucket
            self.human_message_count_hour = 0
        if day_bucket != self.day_bucket:
            self.day_bucket = day_bucket
            self.human_message_count_day = 0
        self.human_message_count_hour += 1
        self.human_message_count_day += 1
        self.last_human_activity_at = at
        self.refresh(at)

    def record_bot_message(self, at: datetime | None = None) -> None:
        self.last_bot_activity_at = at or utcnow()

    def record_ai_analysis(self, at: datetime | None = None) -> None:
        self.last_ai_analysis_at = at or utcnow()

    def cooldown_available(self, now: datetime | None = None) -> bool:
        if self.last_bot_activity_at is None:
            return True
        now = now or utcnow()
        return (now - self.last_bot_activity_at).total_seconds() >= self.cooldown_seconds

    def message_budget_available(self) -> bool:
        return (
            self.human_message_count_hour < self.max_messages_per_hour
            and self.human_message_count_day < self.max_messages_per_day
        )

    def ai_eligibility(self, now: datetime | None = None) -> dict[str, Any]:
        state = self.refresh(now)
        reasons: list[str] = []
        eligible = True

        if not self.enabled:
            eligible = False
            reasons.append("disabled")
        if state == "ACTIVE":
            eligible = False
            reasons.append("human_conversation_active")
        if not self.cooldown_available(now):
            eligible = False
            reasons.append("cooldown")
        if self.last_ai_analysis_at is not None:
            now_check = now or utcnow()
            if (now_check - self.last_ai_analysis_at).total_seconds() < self.cooldown_seconds:
                eligible = False
                reasons.append("ai_analysis_cooldown")
        if not self.message_budget_available():
            eligible = False
            reasons.append("message_budget")

        return {
            "room_name": self.room_name,
            "eligible": eligible,
            "state": state,
            "reasons": reasons,
            "last_human_activity_at": self.last_human_activity_at.isoformat() if self.last_human_activity_at else None,
            "last_bot_activity_at": self.last_bot_activity_at.isoformat() if self.last_bot_activity_at else None,
            "last_ai_analysis_at": self.last_ai_analysis_at.isoformat() if self.last_ai_analysis_at else None,
            "human_message_count_hour": self.human_message_count_hour,
            "human_message_count_day": self.human_message_count_day,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_name": self.room_name,
            "enabled": self.enabled,
            "idle_threshold_seconds": self.idle_threshold_seconds,
            "inactive_threshold_seconds": self.inactive_threshold_seconds,
            "cooldown_seconds": self.cooldown_seconds,
            "max_messages_per_hour": self.max_messages_per_hour,
            "max_messages_per_day": self.max_messages_per_day,
            "last_human_activity_at": self.last_human_activity_at.isoformat() if self.last_human_activity_at else None,
            "last_bot_activity_at": self.last_bot_activity_at.isoformat() if self.last_bot_activity_at else None,
            "activity_state": self.activity_state,
            "human_message_count_hour": self.human_message_count_hour,
            "human_message_count_day": self.human_message_count_day,
        }


class ActivityEngine:
    """Tracks deterministic room activity without making AI decisions."""

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        defaults = defaults or {}
        self.defaults = {
            "enabled": bool(defaults.get("enabled", False)),
            "idle_threshold_seconds": int(defaults.get("idle_threshold_seconds", 900)),
            "inactive_threshold_seconds": int(defaults.get("inactive_threshold_seconds", 3600)),
            "cooldown_seconds": int(defaults.get("cooldown_seconds", 1800)),
            "max_messages_per_hour": int(defaults.get("max_messages_per_hour", 3)),
            "max_messages_per_day": int(defaults.get("max_messages_per_day", 20)),
        }
        self.rooms: dict[str, RoomActivity] = {}

    def get_or_create(self, room_name: str, settings: dict[str, Any] | None = None) -> RoomActivity:
        room = str(room_name or "").strip()
        if not room:
            raise ValueError("room_name is required")
        if room not in self.rooms:
            cfg = dict(self.defaults)
            if settings:
                cfg.update({k: settings[k] for k in cfg if k in settings})
            self.rooms[room] = RoomActivity(room_name=room, **cfg)
        elif settings:
            activity = self.rooms[room]
            for key in self.defaults:
                if key in settings:
                    setattr(activity, key, type(getattr(activity, key))(settings[key]))
        return self.rooms[room]

    def load(self, rows: list[dict[str, Any]]) -> int:
        restored = 0
        for row in rows or []:
            try:
                activity = self.get_or_create(str(row.get("room_name") or ""), row)
                activity.last_human_activity_at = parse_timestamp(row.get("last_human_activity_at"))
                activity.last_bot_activity_at = parse_timestamp(row.get("last_bot_activity_at"))
                activity.last_ai_analysis_at = parse_timestamp(row.get("last_ai_analysis_at"))
                activity.activity_state = str(row.get("activity_state") or "INACTIVE")
                activity.human_message_count_hour = int(row.get("human_message_count_hour") or 0)
                activity.human_message_count_day = int(row.get("human_message_count_day") or 0)
                now = activity.last_human_activity_at or utcnow()
                activity.hour_bucket = now.strftime("%Y-%m-%dT%H")
                activity.day_bucket = now.strftime("%Y-%m-%d")
                activity.refresh()
                restored += 1
            except (TypeError, ValueError):
                continue
        return restored

    def record_human_message(self, room_name: str, at: datetime | None = None, settings: dict[str, Any] | None = None) -> RoomActivity:
        activity = self.get_or_create(room_name, settings)
        activity.record_human_message(at)
        return activity

    def record_bot_message(self, room_name: str, at: datetime | None = None) -> RoomActivity:
        activity = self.get_or_create(room_name)
        activity.record_bot_message(at)
        return activity

    def eligibility(self, room_name: str, now: datetime | None = None, settings: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.get_or_create(room_name, settings).ai_eligibility(now)

    def snapshot(self, room_name: str) -> dict[str, Any]:
        return self.get_or_create(room_name).to_dict()

    def tick(self, now: datetime | None = None) -> list[dict[str, Any]]:
        now = now or utcnow()
        return [activity.ai_eligibility(now) for activity in self.rooms.values()]
