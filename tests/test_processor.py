from app.services.splitter import split_text


def test_splitter_returns_multiple_chunks_for_long_text():
    text = "word " * 3000

    chunks = split_text(text)

    assert len(chunks) >= 2
    assert all(isinstance(chunk, str) and chunk for chunk in chunks)
