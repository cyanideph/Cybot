from ai.room_context import RoomContextManager


def test_room_context_includes_summary_memory_and_recent_messages():
    manager = RoomContextManager(max_recent_messages=3, max_memory_items=2)
    context = manager.build(
        "Cebu",
        [
            {"sender": "alice", "body": "music tonight?"},
            {"sender": "bob", "body": "OPM please"},
            {"sender": "carol", "body": "/HELP"},
        ],
        {"summary": "The room was discussing OPM.", "topic": "OPM"},
        [
            {"content": "Users previously discussed OPM artists."},
            {"content": "The room often plays music quizzes."},
        ],
    )

    prompt = context.prompt_text()
    assert "ROOM: Cebu" in prompt
    assert "TOPIC: OPM" in prompt
    assert "The room was discussing OPM." in prompt
    assert "Users previously discussed OPM artists." in prompt
    assert "alice: music tonight?" in prompt
    assert "carol: /HELP" in prompt


def test_room_context_is_bounded_and_does_not_execute_commands():
    manager = RoomContextManager()
    context = manager.build(
        "Test",
        [{"sender": "user", "body": "x" * 10000}],
    )

    prompt = context.prompt_text(1000)
    assert len(prompt) <= 1000
    assert "/STOP" not in prompt
