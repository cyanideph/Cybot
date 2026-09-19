from ai.observability import summarize_decisions


def test_summarize_decisions():
    result = summarize_decisions([
        {"allowed": True, "reason": "validated_chat", "action": "chat"},
        {"allowed": False, "reason": "low_confidence", "action": "chat"},
        {"allowed": False, "reason": "embedded_command", "action": "chat"},
    ])
    assert result["total"] == 3
    assert result["allowed"] == 1
    assert result["blocked"] == 2
    assert result["allow_rate"] == 1 / 3
    assert result["reasons"] == {
        "embedded_command": 1,
        "low_confidence": 1,
        "validated_chat": 1,
    }
    assert result["actions"] == {"chat": 3}


def test_empty_summary_is_safe():
    result = summarize_decisions([])
    assert result == {
        "total": 0,
        "allowed": 0,
        "blocked": 0,
        "allow_rate": 0.0,
        "reasons": {},
        "actions": {},
    }
