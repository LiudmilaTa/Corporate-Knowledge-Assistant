import pytest

from app.services import rag


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

    with pytest.raises(rag.NoRelevantResultsError) as error:
        rag.ask_question("What is this about?")

    assert error.value.search_candidates == [
        ("test.pdf", 1, 0, "unrelated content", 1.5)
    ]


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


def test_ask_question_with_trace_reports_ollama_stages(monkeypatch):
    monkeypatch.setattr(rag, "create_embedding", lambda question: [0.1, 0.2])
    monkeypatch.setattr(
        rag,
        "search_documents",
        lambda query_embedding, limit=5, **kwargs: [
            ("test.pdf", 1, 0, "relevant content", 0.1),
        ],
    )
    monkeypatch.setattr(
        rag, "translate_search_query", lambda question, sample: "translated question"
    )
    monkeypatch.setattr(rag, "generate_answer", lambda context, question: "The answer")
    progress = []

    rag.ask_question_with_trace(
        "What is this about?",
        filename="test.pdf",
        progress_callback=progress.append,
    )

    assert progress == [
        "embedding question",
        "searching vector index",
        "translating question to document language with Ollama",
        "embedding translated question",
        "searching translated question",
        "generating answer with Ollama",
        "answer generated",
    ]
