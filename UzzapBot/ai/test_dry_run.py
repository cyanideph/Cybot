from ai.dry_run import simulate_decisions


def test_simulation_has_no_side_effects():
    result = simulate_decisions([
        {
            "should_intervene": True,
            "topic": "ANIME",
            "confidence": .95,
            "action": "suggest_game",
            "game": "anime",
            "response": "",
        },
        {
            "should_intervene": True,
            "topic": "GENERAL",
            "confidence": .99,
            "action": "chat",
            "game": None,
            "response": "",
        },
    ])
    assert result["total"] == 2
    assert result["allowed"] == 1
    assert result["blocked"] == 1
    assert result["reasons"]["validated_game_suggestion"] == 1
    assert result["reasons"]["empty_response"] == 1


def test_simulation_reports_safety_reasons():
    result = simulate_decisions([
        {
            "should_intervene": True,
            "topic": "GENERAL",
            "confidence": .99,
            "action": "chat",
            "game": None,
            "response": "Try /STOP now",
        },
        {
            "should_intervene": True,
            "topic": "GENERAL",
            "confidence": .50,
            "action": "chat",
            "game": None,
            "response": "hello",
        },
    ])
    assert result["blocked"] == 2
    assert result["reasons"]["embedded_command"] == 1
    assert result["reasons"]["low_confidence"] == 1
