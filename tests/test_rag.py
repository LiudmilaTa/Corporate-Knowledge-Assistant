from app.services import rag
import pytest

def test_ask_question_raises_when_no_results(monkeypatch):
    monkeypatch.setattr(rag, "create_embedding", lambda question: [0.1, 0.2])
    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda query_embedding, limit=5, **kwargs: [],
    )
    monkeypatch.setattr(rag, "generate_answer", lambda context, question: "No data")

    with pytest.raises(rag.NoDocumentsIndexedError):
        rag.ask_question("What is this about?")


def test_ask_question_raises_when_results_not_relevant(monkeypatch):
    monkeypatch.setattr(rag, "create_embedding", lambda question: [0.1, 0.2])
    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda query_embedding, limit=5, **kwargs: [
            ("test.pdf", 1, 0, "unrelated content", 1.5),
        ],
    )
    monkeypatch.setattr(rag, "generate_answer", lambda context, question: "No data")

    with pytest.raises(rag.NoRelevantResultsError):
        rag.ask_question("What is this about?")


def test_ask_question_returns_answer_for_relevant_results(monkeypatch):
    monkeypatch.setattr(rag, "create_embedding", lambda question: [0.1, 0.2])
    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda query_embedding, limit=5, **kwargs: [
            ("test.pdf", 1, 0, "relevant content", 0.1),
        ],
    )
    monkeypatch.setattr(rag, "generate_answer", lambda context, question: "The answer")

    result = rag.ask_question("What is this about?")

    assert result["answer"] == "The answer"
    assert result["sources"] == [
        {"filename": "test.pdf", "page": 1, "excerpt": "relevant content"}
    ]
