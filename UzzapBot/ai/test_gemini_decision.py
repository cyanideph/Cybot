from ai.gemini_decision import GeminiDecisionClient

def test_empty_decision_is_safe():
    result = GeminiDecisionClient("").decide("")
    assert not result.ok
    assert result.error == "empty_conversation"

def test_missing_key_is_safe():
    result = GeminiDecisionClient("").decide("hello everyone")
    assert not result.ok
    assert "GEMINI_API_KEY" in result.error
