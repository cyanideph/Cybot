from ai.embedding import GeminiEmbedding


def test_empty_embedding_is_safe():
    result = GeminiEmbedding("").embed_room("")
    assert result.ok is False
    assert result.error == "empty_text"


def test_missing_key_is_safe():
    result = GeminiEmbedding("").embed_query("hello room")
    assert result.ok is False
    assert "GEMINI_API_KEY" in result.error


def test_missing_key_is_safe_for_document_embedding():
    result = GeminiEmbedding("").embed_document("room context", "Cebu")
    assert result.ok is False
    assert "GEMINI_API_KEY" in result.error
