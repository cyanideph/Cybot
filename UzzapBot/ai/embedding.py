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

    def _embed(self, text: str, prefix: str) -> EmbeddingResult:
        text = str(text or "").strip()
        if not text:
            return EmbeddingResult(False, error="empty_text")
        try:
            response = self._get_client().models.embed_content(
                model="gemini-embedding-2",
                contents=f"{prefix}{text[-6000:]}",
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
            values = [float(v) for v in values]
            if len(values) != self.output_dimensionality:
                return EmbeddingResult(
                    False,
                    error=f"unexpected_embedding_dimensions:{len(values)}",
                )
            return EmbeddingResult(True, values=values)
        except Exception as exc:
            return EmbeddingResult(False, error=f"{type(exc).__name__}: {exc}")

    def embed_query(self, query: str) -> EmbeddingResult:
        return self._embed(query, "task: search result | query: ")

    def embed_document(self, document: str, title: str = "none") -> EmbeddingResult:
        safe_title = str(title or "none")[:200]
        return self._embed(document, f"title: {safe_title} | text: ")

    def embed_room(self, conversation: str) -> EmbeddingResult:
        return self._embed(conversation, "task: classification | query: ")
