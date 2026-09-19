"""Gemini Flash structured room decision client."""
from __future__ import annotations
import json
from dataclasses import dataclass

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

@dataclass(frozen=True)
class GeminiDecisionResult:
    ok: bool
    decision: dict | None = None
    error: str = ""

class GeminiDecisionClient:
    def __init__(self, api_key: str, model: str = "gemini-3.8-flash") -> None:
        self.api_key = str(api_key or "").strip()
        self.model = model
        self._client = None

    def _get_client(self):
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        if genai is None:
            raise RuntimeError("google-genai is not installed")
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def decide(self, conversation: str) -> GeminiDecisionResult:
        text = str(conversation or "").strip()
        if not text:
            return GeminiDecisionResult(False, error="empty_conversation")
        schema = {
            "type": "object",
            "properties": {
                "should_intervene": {"type": "boolean"},
                "topic": {"type": "string", "enum": [
                    "OPM", "FOREIGN_MUSIC", "ANIME", "MATH", "ALGEBRA",
                    "LOGIC", "ENGLISH_WORDS", "TAGALOG_WORDS", "GENERAL", "OTHER"
                ]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "action": {"type": "string", "enum": ["suggest_game", "chat", "none"]},
                "game": {"type": ["string", "null"]},
                "response": {"type": "string"}
            },
            "required": ["should_intervene", "topic", "confidence", "action", "game", "response"],
            "additionalProperties": False,
        }
        prompt = (
            "You are the decision layer for UzzapBot. Analyze the recent room conversation. "
            "Never invent facts, never claim to be human, and never execute commands. "
            "Only suggest one of the existing Uzzap games. Keep response empty when action is none. "
            "Return only the requested structured result.\n\nRECENT ROOM:\n" + text[-6000:]
        )
        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.1,
                ),
            )
            raw = getattr(response, "text", "") or ""
            decision = json.loads(raw)
            if not isinstance(decision, dict):
                return GeminiDecisionResult(False, error="invalid_decision_shape")
            return GeminiDecisionResult(True, decision=decision)
        except Exception as exc:
            return GeminiDecisionResult(False, error=f"{type(exc).__name__}: {exc}")
