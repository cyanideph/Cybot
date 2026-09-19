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
