import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_engine import GameEngine, Session


def test_reply_rotation_avoids_recent_repeats():
    engine = GameEngine()
    session = Session("test-room", "math", question="2 + 2 = ?", answer="4")
    engine.sessions[session.room] = session

    replies = [
        engine._reply(session, "correct", engine.CORRECT_REPLIES, name="cy", points=10)
        for _ in range(5)
    ]

    assert len(set(replies)) == 5
    assert len(session.reply_history["correct"]) == 4


def test_wrong_answer_returns_feedback_without_revealing_answer():
    engine = GameEngine()
    session = Session("test-room", "math", question="2 + 2 = ?", answer="4")
    engine.sessions[session.room] = session

    correct, response = engine.answer("test-room", "u1", "cy", "cy", "3")

    assert correct is False
    assert response
    assert "4" not in response
    assert session.players["u1"].score == 0
    assert session.players["u1"].attempts == 1
