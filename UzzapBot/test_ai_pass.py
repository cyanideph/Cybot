import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bot as bot_module


class FakeActivityState:
    def __init__(self):
        self.analysis_calls = 0

    def record_ai_analysis(self):
        self.analysis_calls += 1


class FakeActivity:
    def __init__(self):
        self.rooms = {"Cebu": FakeActivityState()}
        self.state = self.rooms["Cebu"]

    def eligibility(self, room_name):
        return {
            "eligible": True,
            "state": "QUIET",
            "reasons": [],
        }

    def get_or_create(self, room_name):
        return self.state

    def snapshot(self, room_name):
        return {
            "room_name": room_name,
            "last_ai_analysis_at": "2026-09-19T12:00:00+00:00",
        }


class FakeDB:
    def __init__(self):
        self.events = []
        self.saved_states = []
        self.sent = []
        self.memories = []
        self.summaries = []
        self.embeddings = []
        self.usage = {"requests_hour": 0, "requests_day": 0, "messages_hour": 0, "messages_day": 0}

    def ai_requests_today(self):
        return self.usage["requests_day"]

    def ai_usage(self, room_name=None):
        return dict(self.usage)

    def recent_room_messages(self, room_name, limit):
        return [{"sender": "alice", "body": "Anime sounds fun"}]

    def save_room_activity(self, state):
        self.saved_states.append(state)

    def save_ai_event(self, event):
        self.events.append(event)

    def load_room_summary(self, room_name):
        return {"room_name": room_name, "summary": "", "topic": "GENERAL", "message_count": 0}

    def load_room_memory(self, room_name, limit):
        return []

    def save_room_memory(self, memory):
        self.memories.append(memory)

    def save_room_summary(self, summary):
        self.summaries.append(summary)

    def semantic_room_memory(self, room_name, query_embedding, threshold, limit):
        return []

    def save_room_memory_embedding(self, memory_id, values):
        self.embeddings.append((memory_id, values))

    def send(self, room_name, body):
        self.sent.append((room_name, body))


class FakeClient:
    def __init__(self, api_key, model):
        pass

    def decide(self, conversation):
        return type("Result", (), {
            "ok": True,
            "decision": {
                "should_intervene": True,
                "topic": "ANIME",
                "confidence": 0.95,
                "action": "suggest_game",
                "game": "anime",
                "response": "Want to play Anime?"
            },
            "error": "",
        })()


class FakeEmbedder:
    def __init__(self, api_key, output_dimensionality):
        self.api_key = api_key
        self.output_dimensionality = output_dimensionality

    def embed_query(self, text):
        return type("Result", (), {"ok": True, "values": [0.1] * self.output_dimensionality})()

    def embed_document(self, text, title="none"):
        return type("Result", (), {"ok": True, "values": [0.2] * self.output_dimensionality})()


def test_run_ai_pass_is_callable_and_dry_run_blocks_send(monkeypatch):
    monkeypatch.setattr(bot_module, "AI_ENABLED", True)
    monkeypatch.setattr(bot_module, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(bot_module, "AI_DRY_RUN", True)
    monkeypatch.setattr(bot_module, "AI_MAX_REQUESTS_PER_DAY", 100)
    monkeypatch.setattr(bot_module, "AI_MIN_CONFIDENCE", 0.75)
    monkeypatch.setattr(bot_module, "GEMINI_FLASH_MODEL", "test-model")
    monkeypatch.setattr(bot_module, "GeminiDecisionClient", FakeClient)
    monkeypatch.setattr(bot_module, "GeminiEmbedding", FakeEmbedder)

    db = FakeDB()
    activity = FakeActivity()

    bot_module.run_ai_pass(db, activity)

    assert activity.state.analysis_calls == 1
    assert db.saved_states
    assert db.events[-1]["allowed"] is True
    assert db.events[-1]["dry_run"] is True
    assert db.sent == []


def test_run_ai_pass_sends_only_after_dry_run_disabled(monkeypatch):
    monkeypatch.setattr(bot_module, "AI_ENABLED", True)
    monkeypatch.setattr(bot_module, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(bot_module, "AI_DRY_RUN", False)
    monkeypatch.setattr(bot_module, "AI_MAX_REQUESTS_PER_DAY", 100)
    monkeypatch.setattr(bot_module, "AI_MIN_CONFIDENCE", 0.75)
    monkeypatch.setattr(bot_module, "GEMINI_FLASH_MODEL", "test-model")
    monkeypatch.setattr(bot_module, "GeminiDecisionClient", FakeClient)

    db = FakeDB()
    activity = FakeActivity()

    bot_module.run_ai_pass(db, activity)

    assert db.sent == [("Cebu", "Want to play Anime?")]
