"""Gemini Embedding 2 wrapper with safe failure behavior."""
from __future__ import annotations
from dataclasses import dataclass

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

@dataclass(frozen=True)
class EmbeddingResult:
    ok: bool
    values: list[float] | None = None
    error: str = ""

class GeminiEmbedding:
    def __init__(self, api_key: str, output_dimensionality: int = 768) -> None:
        self.api_key = str(api_key or "").strip()
        self.output_dimensionality = int(output_dimensionality)
        self._client = None

    def _get_client(self):
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        if genai is None:
            raise RuntimeError("google-genai is not installed")
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed_room(self, conversation: str) -> EmbeddingResult:
        text = str(conversation or "").strip()
        if not text:
            return EmbeddingResult(False, error="empty_conversation")
        try:
            response = self._get_client().models.embed_content(
                model="gemini-embedding-2",
                contents=f"task: classification | query: {text[-6000:]}",
                config=types.EmbedContentConfig(
                    output_dimensionality=self.output_dimensionality
                ),
            )
            embeddings = getattr(response, "embeddings", None) or []
            if not embeddings:
                return EmbeddingResult(False, error="no_embedding")
            values = getattr(embeddings[0], "values", None)
            if not values:
                return EmbeddingResult(False, error="empty_embedding")
            return EmbeddingResult(True, values=[float(v) for v in values])
        except Exception as exc:
            return EmbeddingResult(False, error=f"{type(exc).__name__}: {exc}")
