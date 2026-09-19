import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bot import is_admin, parse_command
from game_engine import GameEngine


@pytest.mark.parametrize(
    "text",
    [
        "",
        "hello",
        "TT ON",
        "!",
        "!!HELP",
        "game start trivia",
        "/",
        "/   ",
    ],
)
def test_only_slash_prefixed_commands_are_parsed(text):
    if text in {"/", "/   "}:
        assert parse_command(text) is None
    elif text.startswith("/"):
        assert parse_command(text)[0] in {"unknown", "invalid_command", "invalid_game_command"}
    else:
        assert parse_command(text) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/help", ["help"]),
        ("/HELP", ["help"]),
        ("/TrIvIa On", ["start", "trivia"]),
        ("/random quiz1", ["start", "random1"]),
        ("/gta foreign", ["start", "gtaforeign"]),
        ("/english wordhunt", ["start", "wordhunt"]),
        ("/tagalog wordhunt", ["start", "summonnight2"]),
        ("/wcbot on", ["wcbot", "on"]),
        ("/wcbot OFF", ["wcbot", "off"]),
        ("/challenge Manila", ["challenge", "Manila"]),
        ("/challenge off", ["challenge_off"]),
        ("/wmsg welcome to Cebu", ["wmsg", "welcome to Cebu"]),
    ],
)
def test_command_parser_is_case_insensitive_but_preserves_message_text(text, expected):
    assert parse_command(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "/help now",
        "/join now",
        "/stop now",
        "/pause now",
        "/resume now",
        "/next now",
        "/reveal now",
        "/activate now",
        "/lock now",
        "/unlock now",
        "/clue now",
        "/status now",
        "/score now",
        "/leaderboard now",
        "/version now",
        "/wcbot maybe",
        "/challenge",
        "/challenge off extra",
        "/trivia",
        "/trivia on extra",
    ],
)
def test_malformed_commands_are_rejected(text):
    parsed = parse_command(text)
    assert parsed[0] in {"invalid_command", "invalid_game_command"}


def test_admin_identity_never_falls_back_to_username():
    assert is_admin({"sender_id": "admin-uuid", "sender": "not-admin"}) is False

    # This monkeypatch-style check is intentionally local to the function's
    # contract: only sender_id may authorize an administrator.
    import bot
    original = bot.ADMIN_IDS
    try:
        bot.ADMIN_IDS = {"admin-uuid"}
        assert is_admin({"sender_id": "admin-uuid", "sender": "anything"}) is True
        assert is_admin({"sender_id": "other", "sender": "admin"}) is False
        assert is_admin({"sender_id": "", "sender": "admin"}) is False
    finally:
        bot.ADMIN_IDS = original


def test_game_join_leave_and_rejoin_state():
    engine = GameEngine()
    session = engine.start("flow-room", "math", 10, 100)

    ok, _ = engine.join("flow-room", "u1", "alice", "Alice")
    assert ok
    assert "u1" in session.players

    ok2, response2 = engine.join("flow-room", "u1", "alice", "Alice")
    assert ok2 is False
    assert "already" in response2.casefold()

    ok3, _ = engine.leave("flow-room", "u1")
    assert ok3
    assert "u1" not in session.players

    ok4, _ = engine.join("flow-room", "u1", "alice", "Alice")
    assert ok4
    assert session.players["u1"].score == 0


def test_answer_flow_updates_score_attempts_and_progresses_question():
    engine = GameEngine()
    session = engine.start("answer-flow", "math", 10, 100)
    engine.join("answer-flow", "u1", "alice", "Alice")
    session.answer = "42"
    session.question = "What is the answer?"

    correct, response = engine.answer("answer-flow", "u1", "alice", "Alice", "42")

    player = session.players["u1"]
    assert correct is True
    assert response
    assert player.attempts == 1
    assert player.correct == 1
    assert player.score == 10
    assert session.number >= 2


def test_wrong_answer_never_awards_points():
    engine = GameEngine()
    session = engine.start("wrong-flow", "math", 10, 100)
    engine.join("wrong-flow", "u1", "alice", "Alice")
    session.answer = "42"

    correct, response = engine.answer("wrong-flow", "u1", "alice", "Alice", "41")

    player = session.players["u1"]
    assert correct is False
    assert response
    assert player.attempts == 1
    assert player.correct == 0
    assert player.score == 0


def test_paused_game_does_not_accept_answers():
    engine = GameEngine()
    session = engine.start("paused-flow", "math", 10, 100)
    engine.join("paused-flow", "u1", "alice", "Alice")
    session.answer = "42"
    session.paused = True

    correct, response = engine.answer("paused-flow", "u1", "alice", "Alice", "42")

    assert correct is False
    assert response == ""
    assert session.players["u1"].score == 0


def test_unjoined_user_cannot_score():
    engine = GameEngine()
    session = engine.start("join-required", "math", 10, 100)
    session.answer = "42"

    correct, response = engine.answer("join-required", "u1", "alice", "Alice", "42")

    assert correct is False
    assert response == ""
    assert session.players == {}


def test_stop_removes_active_session():
    engine = GameEngine()
    engine.start("stop-room", "math", 10, 100)

    engine.stop("stop-room")

    assert engine.get("stop-room") is None


def test_export_restore_preserves_player_and_game_state():
    engine = GameEngine()
    session = engine.start("restore-flow", "trivia", 25, 50, endless=True)
    engine.join("restore-flow", "u1", "alice", "Alice")
    session.players["u1"].score = 25
    session.players["u1"].correct = 2
    session.players["u1"].attempts = 3
    session.clue_level = 2
    session.clue_text = "AB__"
    session.used_questions.add("question-1")

    state = engine.export_state("restore-flow")
    restored = GameEngine().restore_state(state)

    assert restored is not None
    assert restored.room == "restore-flow"
    assert restored.mode == "trivia"
    assert restored.points == 25
    assert restored.limit == 50
    assert restored.endless is True
    assert restored.clue_level == 2
    assert restored.clue_text == "AB__"
    assert "question-1" in restored.used_questions
    assert restored.players["u1"].score == 25
    assert restored.players["u1"].correct == 2
    assert restored.players["u1"].attempts == 3


@pytest.mark.parametrize(
    "state",
    [
        None,
        {},
        {"room": None},
        {"room": "x", "players": [{"not": "a player"}]},
    ],
)
def test_restore_rejects_or_safely_handles_malformed_state(state):
    engine = GameEngine()
    if state in (None, {}, {"room": None}):
        assert engine.restore_state(state) is None
    else:
        restored = engine.restore_state(state)
        assert restored is not None
        assert restored.room == "x"


def test_no_active_game_commands_return_safe_responses():
    engine = GameEngine()

    assert engine.clue("missing") == "[c08]No active game."
    assert engine.repost("missing") == "[c08]No active game."
    assert engine.status("missing") == "[c08]No active game."
    assert engine.score_text("missing", "u1") == "[c08]No active game."
    assert engine.leaderboard_text("missing") == "[c08]No active game."
