import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai.activity_engine import ActivityEngine, RoomActivity


UTC = timezone.utc


def test_room_activity_transitions_active_quiet_inactive():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    activity = RoomActivity("Cebu", idle_threshold_seconds=900, inactive_threshold_seconds=3600)

    activity.record_human_message(now)
    assert activity.activity_state == "ACTIVE"

    assert activity.refresh(now + timedelta(minutes=15)) == "QUIET"
    assert activity.refresh(now + timedelta(hours=1)) == "INACTIVE"


def test_bot_messages_do_not_change_human_activity():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    activity = RoomActivity("Cebu")
    activity.record_human_message(now)
    activity.record_bot_message(now + timedelta(minutes=10))

    assert activity.last_human_activity_at == now
    assert activity.last_bot_activity_at == now + timedelta(minutes=10)


def test_activity_budget_and_cooldown_are_deterministic():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    activity = RoomActivity(
        "Cebu",
        enabled=True,
        idle_threshold_seconds=60,
        inactive_threshold_seconds=300,
        cooldown_seconds=600,
        max_messages_per_hour=3,
        max_messages_per_day=20,
    )

    activity.record_human_message(now)
    activity.record_human_message(now + timedelta(seconds=1))
    activity.record_human_message(now + timedelta(seconds=2))
    activity.record_bot_message(now)

    assert activity.message_budget_available() is False
    assert activity.cooldown_available(now + timedelta(minutes=5)) is False
    assert activity.cooldown_available(now + timedelta(minutes=10)) is True


def test_ai_is_never_eligible_while_humans_are_active():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    engine = ActivityEngine({"enabled": True, "idle_threshold_seconds": 900})

    engine.record_human_message("Cebu", now)
    decision = engine.eligibility("Cebu", now + timedelta(minutes=5))

    assert decision["eligible"] is False
    assert "human_conversation_active" in decision["reasons"]


def test_disabled_by_default():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    engine = ActivityEngine()
    engine.record_human_message("Cebu", now)

    decision = engine.eligibility("Cebu", now + timedelta(minutes=20))
    assert decision["eligible"] is False
    assert "disabled" in decision["reasons"]


def test_activity_engine_loads_persisted_state():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    engine = ActivityEngine({"enabled": True})
    restored = engine.load([{
        "room_name": "Cebu",
        "enabled": True,
        "last_human_activity_at": now.isoformat(),
        "last_bot_activity_at": None,
        "activity_state": "ACTIVE",
        "human_message_count_hour": 2,
        "human_message_count_day": 4,
    }])

    assert restored == 1
    snapshot = engine.snapshot("Cebu")
    assert snapshot["human_message_count_hour"] == 2
    assert snapshot["human_message_count_day"] == 4


def test_ai_eligibility_does_not_use_human_message_budget():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    activity = RoomActivity(
        "Cebu",
        enabled=True,
        idle_threshold_seconds=60,
        inactive_threshold_seconds=300,
        cooldown_seconds=600,
        max_messages_per_hour=3,
        max_messages_per_day=20,
    )
    for offset in range(3):
        activity.record_human_message(now - timedelta(seconds=30 + offset))
    decision = activity.ai_eligibility(now)
    assert decision["state"] == "QUIET"
    assert decision["eligible"] is True


def test_activity_snapshot_and_restore_keep_ai_analysis_timestamp():
    now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    analysis_at = now - timedelta(minutes=5)
    engine = ActivityEngine({"enabled": True})
    activity = engine.get_or_create("Cebu")
    activity.last_ai_analysis_at = analysis_at

    snapshot = engine.snapshot("Cebu")
    assert snapshot["last_ai_analysis_at"] == analysis_at.isoformat()

    restored_engine = ActivityEngine({"enabled": True})
    assert restored_engine.load([snapshot]) == 1
    assert restored_engine.snapshot("Cebu")["last_ai_analysis_at"] == analysis_at.isoformat()
