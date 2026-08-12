from app.services import rag

def test_ask_question_returns_empty_sources_when_no_results(monkeypatch):
    monkeypatch.setattr(rag, "create_embedding", lambda question: [0.1, 0.2])
    monkeypatch.setattr(rag, "search_documents", lambda query_embedding, limit=5: [])
    monkeypatch.setattr(rag, "generate_answer", lambda context, question: "No data")

    result = rag.ask_question("What is this about?")

    assert result["answer"] == "No data"
    assert result["sources"] == []
