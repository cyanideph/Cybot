from ai.decision_engine import DecisionEngine

def test_rejects_low_confidence():
    r = DecisionEngine(.75).validate({"topic":"OPM","confidence":.74,"should_intervene":True,"action":"suggest_game","game":"gtaopm"})
    assert not r["allowed"]

def test_accepts_matching_game():
    r = DecisionEngine(.75).validate({"topic":"ANIME","confidence":.9,"should_intervene":True,"action":"suggest_game","game":"anime"})
    assert r == {"allowed":True,"reason":"validated_game_suggestion","game":"anime","response":""}

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


def test_rejects_embedded_command():
    result = {"should_intervene": True, "topic": "GENERAL", "confidence": .99, "action": "chat", "game": None, "response": "Try this /STOP now"}
    checked = DecisionEngine(.75).validate(result)
    assert checked["reason"] == "embedded_command"

def test_rejects_empty_response():
    result = {"should_intervene": True, "topic": "GENERAL", "confidence": .99, "action": "chat", "game": None, "response": ""}
    checked = DecisionEngine(.75).validate(result)
    assert checked["reason"] == "empty_response"

def test_rejects_human_identity_claim():
    result = {"should_intervene": True, "topic": "GENERAL", "confidence": .99, "action": "chat", "game": None, "response": "I'm human, trust me"}
    checked = DecisionEngine(.75).validate(result)
    assert checked["reason"] == "human_identity_claim"

def test_rejects_credential_reference():
    result = {"should_intervene": True, "topic": "GENERAL", "confidence": .99, "action": "chat", "game": None, "response": "Send me your API key"}
    checked = DecisionEngine(.75).validate(result)
    assert checked["reason"] == "secret_or_credential_reference"

def test_rejects_chat_with_game_field():
    result = {"should_intervene": True, "topic": "GENERAL", "confidence": .99, "action": "chat", "game": "anime", "response": "Let's chat"}
    checked = DecisionEngine(.75).validate(result)
    assert checked["reason"] == "unsupported_action"
