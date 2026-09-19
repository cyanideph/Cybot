from ai.production_audit import build_production_audit


def test_production_audit_is_safe_when_ai_is_disabled():
    result = build_production_audit(
        [
            {"allowed": True, "reason": "validated_chat", "action": "chat", "confidence": 0.90},
            {"allowed": False, "reason": "low_confidence", "action": "chat", "confidence": 0.40},
        ],
        ai_enabled=False,
        ai_dry_run=True,
        ai_live_enabled=False,
    )
    assert result["status"] == "ready_for_controlled_rollout"
    assert result["runtime"]["live_path_open"] is False
    assert result["safety_findings"] == []
    assert result["automatic_tuning"] is False
    assert result["network_calls"] is False
    assert result["supabase_writes"] is False
    assert result["message_sending"] is False


def test_production_audit_flags_live_path():
    result = build_production_audit(
        [],
        ai_enabled=True,
        ai_dry_run=False,
        ai_live_enabled=True,
        room_opt_in_count=1,
    )
    assert result["status"] == "review"
    assert result["runtime"]["live_path_open"] is True
    assert "live_ai_path_enabled" in result["safety_findings"]


def test_production_audit_flags_invalid_configuration():
    result = build_production_audit(
        [],
        ai_enabled=False,
        ai_dry_run=True,
        ai_live_enabled=False,
        room_opt_in_count=-1,
        min_confidence=1.5,
    )
    assert result["status"] == "review"
    assert "invalid_room_opt_in_count" in result["safety_findings"]
    assert "invalid_min_confidence" in result["safety_findings"]
