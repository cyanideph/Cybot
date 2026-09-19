from ai.decision_engine import DecisionEngine

def test_rejects_low_confidence():
    r = DecisionEngine(.75).validate({"topic":"OPM","confidence":.74,"should_intervene":True,"action":"suggest_game","game":"gtaopm"})
    assert not r["allowed"]

def test_accepts_matching_game():
    r = DecisionEngine(.75).validate({"topic":"ANIME","confidence":.9,"should_intervene":True,"action":"suggest_game","game":"anime"})
    assert r == {"allowed":True,"reason":"validated_game_suggestion","game":"anime"}

def test_rejects_ai_game_redirect():
    r = DecisionEngine(.75).validate({"topic":"OPM","confidence":.95,"should_intervene":True,"action":"suggest_game","game":"anime"})
    assert not r["allowed"]

def test_rejects_unsupported_action():
    r = DecisionEngine(.75).validate({"topic":"GENERAL","confidence":.99,"should_intervene":True,"action":"suggest_game","game":None})
    assert not r["allowed"]


def test_rejects_command_like_ai_response():
    result = {
        "should_intervene": True, "topic": "OPM", "confidence": 0.99,
        "action": "suggest_game", "game": "gtaopm", "response": "/STOP"
    }
    checked = DecisionEngine(0.75).validate(result)
    assert checked["allowed"] is False
    assert checked["reason"] == "command_like_response"

def test_rejects_oversized_ai_response():
    result = {
        "should_intervene": True, "topic": "GENERAL", "confidence": 0.99,
        "action": "chat", "game": None, "response": "x" * 501
    }
    checked = DecisionEngine(0.75).validate(result)
    assert checked["allowed"] is False
    assert checked["reason"] == "response_too_long"
