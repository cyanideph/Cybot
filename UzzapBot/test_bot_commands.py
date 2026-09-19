import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bot import parse_command


def test_one_official_command_per_game():
    expected = {
        "/TT ON": ["start", "twist"],
        "/MATH ON": ["start", "math"],
        "/TRIVIA ON": ["start", "trivia"],
        "/ANIME ON": ["start", "anime"],
        "/LOGIC ON": ["start", "logic"],
        "/ALGEBRA ON": ["start", "algebra"],
        "/PH ON": ["start", "filipino"],
        "/RANDOM QUIZ1": ["start", "random1"],
        "/RANDOM QUIZ2": ["start", "random2"],
        "/RANDOM QUIZ3": ["start", "random3"],
        "/RANDOM GTA": ["start", "randomgta"],
        "/GTA OPM": ["start", "gtaopm"],
        "/GTA FOREIGN": ["start", "gtaforeign"],
        "/ENGLISH WORDHUNT": ["start", "wordhunt"],
        "/TAGALOG WORDHUNT": ["start", "summonnight2"],
    }
    for command, result in expected.items():
        assert parse_command(command) == result


def test_duplicate_game_routes_are_rejected():
    for command in (
        "/game start trivia",
        "/game on trivia",
        "/TRIVIA",
        "/trivia on 1 10",
        "/game random quiz1",
        "/game start gtaopm",
        "/TRIVIA ON 1 10",
        "/game start twist",
    ):
        parsed = parse_command(command)
        assert parsed and parsed[0] in {"unknown", "invalid_command", "invalid_game_command"}


def test_single_player_commands():
    for command in ("/HELP", "/CLUE", "/REPOST", "/STATUS", "/SCORE", "/LEADERBOARD", "/VERSION"):
        assert parse_command(command) == [command[1:].casefold()]


def test_single_admin_commands():
    for command in ("/STOP", "/PAUSE", "/RESUME", "/NEXT", "/REVEAL", "/ACTIVATE", "/LOCK", "/UNLOCK"):
        assert parse_command(command) == [command[1:].casefold()]


def test_wcbot_and_challenge_are_single_command_families():
    assert parse_command("/WCBOT ON") == ["wcbot", "on"]
    assert parse_command("/WCBOT OFF") == ["wcbot", "off"]
    assert parse_command("/CHALLENGE Cebu") == ["challenge", "Cebu"]
    assert parse_command("/CHALLENGE OFF") == ["challenge_off"]


def test_non_slash_is_not_a_command():
    assert parse_command("TT ON") is None


def test_bare_slash_is_ignored():
    assert parse_command("/") is None
    assert parse_command("/   ") is None


def test_challenge_off_rejects_extra_words():
    assert parse_command("/CHALLENGE off now") == ["invalid_command", "challenge"]
    assert parse_command("/CHALLENGE OFF") == ["challenge_off"]


def test_admin_authorization_uses_auth_user_id_only(monkeypatch):
    from bot import is_admin
    monkeypatch.setattr("bot.ADMIN_IDS", {"admin-uuid"})
    assert is_admin({"sender_id": "admin-uuid", "sender": "anything"})
    assert not is_admin({"sender_id": "other-uuid", "sender": "admin"})
    assert not is_admin({"sender_id": "", "sender": "admin"})
