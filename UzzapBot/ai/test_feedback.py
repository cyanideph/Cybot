from ai.feedback import evaluate_feedback


def test_feedback_reports_healthy_decisions():
    result = evaluate_feedback([
        {"allowed": True, "reason": "validated_chat", "confidence": 0.90},
        {"allowed": True, "reason": "validated_chat", "confidence": 0.80},
        {"allowed": False, "reason": "low_confidence", "confidence": 0.40},
    ])
    assert result["total"] == 3
    assert result["allowed"] == 2
    assert result["blocked"] == 1
    assert result["block_rate"] == 1 / 3
    assert result["mean_confidence"] == 0.70
    assert result["low_confidence"] == 1
    assert result["feedback"] == "healthy"


def test_feedback_requests_review_when_block_rate_is_high():
    result = evaluate_feedback(
        [
            {"allowed": False, "reason": "embedded_command", "confidence": 0.90},
            {"allowed": False, "reason": "low_confidence", "confidence": 0.40},
            {"allowed": True, "reason": "validated_chat", "confidence": 0.95},
        ],
        max_block_rate=0.50,
    )
    assert result["block_rate"] == 2 / 3
    assert result["feedback"] == "review"


def test_feedback_is_safe_for_empty_or_invalid_confidence():
    result = evaluate_feedback([
        {"allowed": False, "reason": "invalid_result", "confidence": "bad"},
    ])
    assert result["mean_confidence"] == 0.0
    assert result["feedback"] == "review"

    empty = evaluate_feedback([])
    assert empty["feedback"] == "insufficient_data"
