"""Safety-first validation of AI decisions."""
from __future__ import annotations
from typing import Any
from .topic_matcher import match_topic

class DecisionEngine:
    def __init__(self, min_confidence: float = 0.75) -> None:
        self.min_confidence = float(min_confidence)

    def validate(self, result: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(result, dict):
            return {"allowed": False, "reason": "invalid_result", "game": None}
        try:
            confidence = float(result.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0.0
        if not 0 <= confidence <= 1:
            return {"allowed": False, "reason": "invalid_confidence", "game": None}
        if confidence < self.min_confidence:
            return {"allowed": False, "reason": "low_confidence", "game": None}
        if result.get("should_intervene") is not True:
            return {"allowed": False, "reason": "ai_declined", "game": None}
        game = match_topic(result)
        response = str(result.get("response") or "").strip()
        if len(response) > 500:
            return {"allowed": False, "reason": "response_too_long", "game": None}
        if response.startswith("/"):
            return {"allowed": False, "reason": "command_like_response", "game": None}
        if result.get("action") == "suggest_game" and game:
            return {"allowed": True, "reason": "validated_game_suggestion", "game": game, "response": response}
        if result.get("action") == "chat":
            return {"allowed": True, "reason": "validated_chat", "game": None, "response": response}
        return {"allowed": False, "reason": "unsupported_action", "game": None}
