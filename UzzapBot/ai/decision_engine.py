"""Safety-first validation of AI decisions."""
from __future__ import annotations
import re
from typing import Any
from .topic_matcher import match_topic

_COMMAND_RE = re.compile(r"(^|[\\s])/[A-Za-z][A-Za-z0-9_]*(?:\\s|$)")
_UNSAFE_CLAIM_RE = re.compile(
    r"\\b(?:i am human|i'm human|i am a person|i'm a person|as a human|as a person)\\b",
    re.IGNORECASE,
)
_SECRET_RE = re.compile(
    r"\\b(?:password|api[ _-]?key|secret key|access token|refresh token|private key)\\b",
    re.IGNORECASE,
)

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

        action = str(result.get("action") or "").strip().casefold()
        game = match_topic(result)
        response = str(result.get("response") or "").strip()

        if len(response) > 500:
            return {"allowed": False, "reason": "response_too_long", "game": None}
        if not response:
            return {"allowed": False, "reason": "empty_response", "game": None}
        if response.startswith("/"):
            return {"allowed": False, "reason": "command_like_response", "game": None}
        if _COMMAND_RE.search(response):
            return {"allowed": False, "reason": "embedded_command", "game": None}
        if _UNSAFE_CLAIM_RE.search(response):
            return {"allowed": False, "reason": "human_identity_claim", "game": None}
        if _SECRET_RE.search(response):
            return {"allowed": False, "reason": "secret_or_credential_reference", "game": None}

        if action == "suggest_game" and game:
            return {"allowed": True, "reason": "validated_game_suggestion", "game": game, "response": response}
        if action == "chat" and result.get("game") in (None, ""):
            return {"allowed": True, "reason": "validated_chat", "game": None, "response": response}
        return {"allowed": False, "reason": "unsupported_action", "game": None}
