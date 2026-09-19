from ai.embedding import GeminiEmbedding

def test_empty_embedding_is_safe():
    result = GeminiEmbedding("").embed_room("")
    assert result.ok is False
    assert result.error == "empty_conversation"

def test_missing_key_is_safe():
    result = GeminiEmbedding("").embed_room("hello room")
    assert result.ok is False
    assert "GEMINI_API_KEY" in result.error
