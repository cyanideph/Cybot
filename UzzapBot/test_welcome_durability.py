import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import Database


class Response:
    def __init__(self, data=None):
        self.data = data


class Query:
    def __init__(self, client, table):
        self.client = client
        self.table = table
        self.gt_value = None
        self.limit_value = None

    def select(self, *_args):
        return self

    def gt(self, _column, value):
        self.gt_value = value
        return self

    def eq(self, _column, value):
        self.eq_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def execute(self):
        if self.table == "room_participants":
            return Response(self.client.participants)
        if self.table == "uzzapbot_room_settings":
            room = getattr(self, "eq_value", None)
            return Response([self.client.settings[room]] if room in self.client.settings else [])
        return Response([])


class Rpc:
    def __init__(self, client, name, args):
        self.client = client
        self.name = name
        self.args = args

    def execute(self):
        if self.name == "uzzapbot_claim_welcome":
            key = (self.args["p_room_name"], self.args["p_username"].casefold())
            if key in self.client.claimed:
                return Response(False)
            self.client.claimed.add(key)
            return Response(True)
        return Response(None)


class Client:
    def __init__(self):
        self.participants = []
        self.settings = {}
        self.claimed = set()

    def table(self, name):
        return Query(self, name)

    def rpc(self, name, args):
        return Rpc(self, name, args)


def make_db(client):
    db = Database.__new__(Database)
    db.client = client
    return db


def participant(room="Cebu", username="Alice"):
    return {"room_name": room, "username": username, "last_ping": "2026-09-19T12:00:00Z"}


def test_welcome_claim_is_durable_and_idempotent():
    client = Client()
    db = make_db(client)

    assert db.claim_welcome("Cebu", "Alice") is True
    assert db.claim_welcome("Cebu", "alice") is False


def test_poll_new_participants_only_claims_when_wcbot_is_enabled():
    client = Client()
    client.participants = [participant()]
    client.settings["Cebu"] = {"room_name": "Cebu", "wcbot": False}
    db = make_db(client)
    seen = set()

    assert db.poll_new_participants(seen) == []
    assert client.claimed == set()

    client.settings["Cebu"]["wcbot"] = True
    assert db.poll_new_participants(seen) == [client.participants[0]]
    assert client.claimed == {("Cebu", "alice")}


def test_poll_new_participants_does_not_welcome_again_after_restart():
    client = Client()
    client.participants = [participant()]
    client.settings["Cebu"] = {"room_name": "Cebu", "wcbot": True}
    db = make_db(client)

    assert db.poll_new_participants(set()) == [client.participants[0]]

    # Simulate a process restart: a new in-memory seen set, same database.
    assert db.poll_new_participants(set()) == []
