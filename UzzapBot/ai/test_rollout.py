from ai.rollout import evaluate_rollout, rollback_plan


def test_defaults_are_disabled_and_not_activated():
    result = evaluate_rollout({})
    assert result["ready"] is True
    assert result["requested_stage"] == "disabled"
    assert result["runtime_activation"] is False
    assert result["live_path_open"] is False


def test_invalid_stage_fails_closed():
    result = evaluate_rollout({"rollout_stage": "experimental"})
    assert result["ready"] is False
    assert "invalid_rollout_stage" in result["findings"]
    assert result["requested_stage"] == "disabled"


def test_canary_requires_security_and_global_enable():
    result = evaluate_rollout(
        {"rollout_stage": "canary", "canary_percent": 5, "ai_enabled": False}
    )
    assert result["ready"] is False
    assert "global_ai_enable_required" in result["findings"]


def test_canary_percent_is_bounded():
    result = evaluate_rollout(
        {"rollout_stage": "canary", "canary_percent": 11, "ai_enabled": True}
    )
    assert result["ready"] is False
    assert "invalid_canary_percent" in result["findings"]


def test_live_requires_explicit_live_enable_and_no_dry_run():
    result = evaluate_rollout(
        {
            "rollout_stage": "live",
            "ai_enabled": True,
            "ai_live_enabled": False,
            "ai_dry_run": True,
        }
    )
    assert result["ready"] is False
    assert "live_enable_required" in result["findings"]
    assert "dry_run_must_be_disabled" in result["findings"]


def test_rollback_is_disabled_only():
    assert rollback_plan()["target_stage"] == "disabled"
