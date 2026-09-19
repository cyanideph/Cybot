from ai.conversation_replay import replay_decisions


def test_replay_pairs_messages_and_decisions_without_side_effects():
    result = replay_decisions(
        [
            {"sender": "alice", "message": "anime tonight?"},
            {"sender": "bob", "message": "hello"},
        ],
        [
            {
                "should_intervene": True,
                "topic": "ANIME",
                "confidence": 0.95,
                "action": "suggest_game",
                "game": "anime",
                "response": "",
            },
            {
                "should_intervene": True,
                "topic": "GENERAL",
                "confidence": 0.99,
                "action": "chat",
                "game": None,
                "response": "hello!",
            },
        ],
    )
    assert result["messages"] == 2
    assert result["decisions"] == 2
    assert result["simulation"]["allowed"] == 2
    assert result["summary"]["total"] == 2
    assert result["observations"][0]["sender"] == "alice"
    assert result["observations"][0]["message"] == "anime tonight?"


def test_replay_does_not_require_a_message_for_every_decision():
    result = replay_decisions(
        [{"sender": "alice", "message": "hello"}],
        [
            {
                "should_intervene": True,
                "topic": "GENERAL",
                "confidence": 0.99,
                "action": "chat",
                "game": None,
                "response": "hi",
            },
            {
                "should_intervene": True,
                "topic": "GENERAL",
                "confidence": 0.99,
                "action": "chat",
                "game": None,
                "response": "there",
            },
        ],
    )
    assert result["decisions"] == 2
    assert result["observations"][1]["sender"] == ""
    assert result["observations"][1]["message"] == ""
