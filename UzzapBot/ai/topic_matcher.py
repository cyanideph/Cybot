"""Deterministic mapping from AI topics to existing Uzzap games."""
from __future__ import annotations

TOPIC_TO_GAME = {
    "OPM": "gtaopm",
    "FOREIGN_MUSIC": "gtaforeign",
    "ANIME": "anime",
    "MATH": "math",
    "ALGEBRA": "algebra",
    "LOGIC": "logic",
    "ENGLISH_WORDS": "wordhunt",
    "TAGALOG_WORDS": "summonnight2",
}

def match_topic(result: dict) -> str | None:
    topic = str(result.get("topic") or "").upper()
    expected = TOPIC_TO_GAME.get(topic)
    if expected is None:
        return None
    suggested = result.get("game")
    return expected if suggested in (None, expected) else None
