import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import Database


class FakeResponse:
    def __init__(self, data=None):
        self.data = data


class FakeQuery:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.mode = "select"
        self.gt_value = None

    def select(self, *_args):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def gt(self, _column, value):
        self.gt_value = int(value)
        return self

    def eq(self, *_args):
        return self

    def upsert(self, payload, on_conflict=None):
        self.client.upsert_payload = payload
        self.client.upsert_conflict = on_conflict
        return self

    def delete(self):
        self.mode = "delete"
        return self

    def execute(self):
        if self.mode == "delete":
            self.client.deleted = True
            return FakeResponse([])
        if self.table_name == "room_messages":
            if self.gt_value is None:
                rows = [{"id": self.client.latest_id}]
            else:
                rows = [r for r in self.client.messages if int(r["id"]) > self.gt_value]
                rows = rows[:getattr(self, "limit_value", 100)]
            return FakeResponse(rows)
        if self.table_name == "uzzapbot_room_settings":
            return FakeResponse(self.client.room_settings)
        if self.table_name == "room_participants":
            return FakeResponse(self.client.participants)
        if self.table_name == "profiles":
            return FakeResponse(self.client.profile_rows)
        if self.table_name == "game_sessions":
            return FakeResponse(self.client.sessions)
        if self.table_name == "game_players":
            return FakeResponse(self.client.players)
        return FakeResponse([])


class FakeRpc:
    def __init__(self, client, name, args):
        self.client = client
        self.name = name
        self.args = args

    def execute(self):
        self.client.rpc_calls.append((self.name, self.args))
        if self.name == "uzzapbot_get_cursor":
            return FakeResponse(self.client.cursor)
        if self.name == "uzzapbot_advance_cursor":
            previous_id = int(self.args["p_previous_id"])
            message_id = int(self.args["p_message_id"])
            if previous_id != self.client.cursor:
                return FakeResponse(False)
            if message_id <= previous_id:
                return FakeResponse(False)
            self.client.cursor = message_id
            return FakeResponse(True)
        if self.name == "uzzapbot_claim_message":
            message_id = int(self.args["p_message_id"])
            if message_id in self.client.claim_exceptions:
                raise RuntimeError("temporary claim failure")
            return FakeResponse(message_id in self.client.claimable_ids)
        if self.name == "uzzapbot_save_game_state":
            return FakeResponse(self.client.saved_session_id)
        if self.name == "room_bot_message":
            return FakeResponse({"ok": True})
        return FakeResponse(None)


class FakeClient:
    def __init__(self):
        self.latest_id = 0
        self.cursor = 0
        self.messages = []
        self.claimable_ids = set()
        self.claim_exceptions = set()
        self.room_settings = []
        self.participants = []
        self.profile_rows = []
        self.sessions = []
        self.players = []
        self.rpc_calls = []
        self.saved_session_id = 42
        self.upsert_payload = None
        self.upsert_conflict = None
        self.deleted = False

    def table(self, name):
        return FakeQuery(self, name)

    def rpc(self, name, args):
        return FakeRpc(self, name, args)


def make_db(client):
    db = Database.__new__(Database)
    db.client = client
    db.last_id = client.cursor
    return db


def message(message_id, sender="alice", sender_id="user-1", body="hello"):
    return {
        "id": message_id,
        "room_name": "Cebu",
        "sender": sender,
        "body": body,
        "is_system": False,
        "created_at": "2026-09-19T00:00:00Z",
        "sender_id": sender_id,
    }


def test_poll_messages_drains_more_than_one_page_without_skipping(monkeypatch):
    monkeypatch.setattr("database.BOT_SENDER_ID", "bot-uuid")
    client = FakeClient()
    client.messages = [message(i) for i in range(1, 106)]
    client.claimable_ids = set(range(1, 106))
    db = make_db(client)

    rows = db.poll_messages()

    assert len(rows) == 105
    assert [row["id"] for row in rows] == list(range(1, 106))
    assert db.last_id == 105
    assert client.cursor == 105
    assert [call[1]["p_message_id"] for call in client.rpc_calls if call[0] == "uzzapbot_claim_message"] == list(range(1, 106))


def test_poll_messages_stops_at_claim_failure_and_preserves_cursor(monkeypatch):
    monkeypatch.setattr("database.BOT_SENDER_ID", "bot-uuid")
    client = FakeClient()
    client.messages = [message(1), message(2), message(3)]
    client.claimable_ids = {1, 2, 3}
    client.claim_exceptions = {2}
    db = make_db(client)

    with pytest.raises(RuntimeError, match="temporary claim failure"):
        db.poll_messages()

    assert db.last_id == 1
    assert client.cursor == 1

    client.claim_exceptions.clear()
    rows = db.poll_messages()

    assert [row["id"] for row in rows] == [2, 3]
    assert db.last_id == 3
    assert client.cursor == 3


def test_poll_messages_does_not_skip_when_cursor_advance_fails(monkeypatch):
    monkeypatch.setattr("database.BOT_SENDER_ID", "bot-uuid")
    client = FakeClient()
    client.messages = [message(1), message(2)]
    client.claimable_ids = {1, 2}
    db = make_db(client)

    original_rpc = client.rpc
    failed_once = {"value": True}

    def rpc(name, args):
        if name == "uzzapbot_advance_cursor" and failed_once["value"]:
            failed_once["value"] = False
            raise RuntimeError("cursor unavailable")
        return original_rpc(name, args)

    client.rpc = rpc

    with pytest.raises(RuntimeError, match="cursor unavailable"):
        db.poll_messages()

    assert db.last_id == 0
    assert client.cursor == 0

    rows = db.poll_messages()
    assert [row["id"] for row in rows] == [1, 2]
    assert db.last_id == 2


def test_poll_messages_ignores_bot_messages(monkeypatch):
    monkeypatch.setattr("database.BOT_SENDER_ID", "bot-uuid")
    client = FakeClient()
    client.messages = [
        message(1, sender="alice", sender_id="user-1"),
        message(2, sender="uzzapbot", sender_id="other"),
        message(3, sender="bob", sender_id="user-2"),
        message(4, sender="someone", sender_id="bot-uuid"),
    ]
    client.claimable_ids = {1, 2, 3, 4}
    db = make_db(client)

    rows = db.poll_messages()

    assert [row["id"] for row in rows] == [1, 3]
    assert db.last_id == 4


def test_poll_messages_only_returns_successfully_claimed_rows():
    client = FakeClient()
    client.messages = [message(1), message(2), message(3)]
    client.claimable_ids = {1, 3}
    db = make_db(client)

    rows = db.poll_messages()

    assert [row["id"] for row in rows] == [1, 3]
    assert db.last_id == 3


def test_claim_message_uses_atomic_rpc():
    client = FakeClient()
    client.claimable_ids = {7}
    db = make_db(client)

    assert db.claim_message(7) is True
    assert client.rpc_calls == [("uzzapbot_claim_message", {"p_message_id": 7})]


def test_send_uses_server_side_room_bot_rpc_and_preserves_body():
    client = FakeClient()
    db = make_db(client)

    db.send("Cebu", "[c03]Hello :)")

    assert client.rpc_calls == [
        (
            "room_bot_message",
            {"p_room": "Cebu", "p_body": "[c03]Hello :)", "p_is_system": False},
        )
    ]


def test_room_settings_defaults_are_safe():
    client = FakeClient()
    client.room_settings = []
    db = make_db(client)

    assert db.get_room_settings("Cebu") == {
        "activated": False,
        "locked": False,
        "wcbot": False,
        "welcome_message": "welcome to {room} {nickname}",
        "challenge_room": "",
        "ai_enabled": False,
    }


def test_room_settings_round_trip_payload_is_normalized():
    client = FakeClient()
    db = make_db(client)

    db.save_room_settings(
        "Cebu",
        {
            "activated": 1,
            "locked": "",
            "wcbot": True,
            "welcome_message": None,
            "challenge_room": None,
        },
    )

    assert client.upsert_payload == {
        "room_name": "Cebu",
        "activated": True,
        "locked": False,
        "wcbot": True,
        "welcome_message": "welcome to {room} {nickname}",
        "challenge_room": "",
        "ai_enabled": False,
    }
    assert client.upsert_conflict == "room_name"


def test_load_game_state_attaches_players_to_each_session():
    client = FakeClient()
    client.sessions = [
        {
            "id": 1,
            "room_name": "Cebu",
            "game": "math",
            "mode": "math",
            "current_game": "math",
            "points": 10,
            "limit_count": 100,
            "endless": False,
            "paused": False,
            "question_number": 2,
            "question": "2 + 2 = ?",
            "answer": "4",
            "clue_text": "",
            "used_questions": [],
            "state_json": {},
        },
        {
            "id": 2,
            "room_name": "Manila",
            "game": "trivia",
            "mode": "trivia",
            "current_game": "trivia",
            "points": 10,
            "limit_count": 100,
            "endless": False,
            "paused": True,
            "question_number": 5,
            "question": "Q",
            "answer": "A",
            "clue_text": "",
            "used_questions": [],
            "state_json": {"room": "Manila", "game": "trivia", "custom": True},
        },
    ]
    client.players = [
        {"session_id": 1, "user_id": "u1", "username": "alice", "nickname": "Alice", "score": 10, "correct": 1, "attempts": 1},
        {"session_id": 2, "user_id": "u2", "username": "bob", "nickname": "Bob", "score": 20, "correct": 2, "attempts": 3},
    ]
    db = make_db(client)

    states = db.load_game_state()

    assert len(states) == 2
    assert states[0]["room"] == "Cebu"
    assert states[0]["players"][0]["user_id"] == "u1"
    assert states[1]["custom"] is True
    assert states[1]["players"][0]["user_id"] == "u2"


def test_save_game_state_requires_session_id():
    client = FakeClient()
    client.saved_session_id = None
    db = make_db(client)

    with pytest.raises(RuntimeError, match="no session id"):
        db.save_game_state({"room": "Cebu"})


def test_save_game_state_returns_integer_session_id():
    client = FakeClient()
    client.saved_session_id = 123
    db = make_db(client)

    assert db.save_game_state({"room": "Cebu"}) == 123


def test_delete_game_state_targets_room():
    client = FakeClient()
    db = make_db(client)

    db.delete_game_state("Cebu")

    assert client.deleted is True
