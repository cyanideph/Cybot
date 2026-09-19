from ai.security import sanitize_ai_metadata, validate_ai_security_config


def test_security_defaults_are_safe():
    result = validate_ai_security_config(
        {
            "ai_enabled": False,
            "ai_dry_run": True,
            "ai_live_enabled": False,
        }
    )
    assert result["safe"] is True
    assert result["live_path_open"] is False
    assert result["network_calls"] is False
    assert result["supabase_writes"] is False
    assert result["automatic_tuning"] is False


def test_security_rejects_conflicting_live_configuration():
    result = validate_ai_security_config(
        {
            "ai_enabled": True,
            "ai_dry_run": True,
            "ai_live_enabled": True,
        }
    )
    assert result["safe"] is False
    assert "conflicting_live_and_dry_run" in result["findings"]


def test_security_rejects_live_without_global_enable():
    result = validate_ai_security_config(
        {
            "ai_enabled": False,
            "ai_dry_run": False,
            "ai_live_enabled": True,
        }
    )
    assert result["safe"] is False
    assert "live_enabled_without_ai_enabled" in result["findings"]


def test_metadata_sanitizer_drops_secrets():
    result = sanitize_ai_metadata(
        {
            "room": "Cavite",
            "action": "chat",
            "confidence": 0.9,
            "model": "test-model",
            "api_key": "secret",
            "prompt": "private",
        }
    )
    assert result == {
        "room": "Cavite",
        "action": "chat",
        "confidence": 0.9,
        "model": "test-model",
    }
