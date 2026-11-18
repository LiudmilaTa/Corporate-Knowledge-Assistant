from types import SimpleNamespace

import pytest

from app.mcp import tools


def test_search_knowledge_returns_retrieved_chunks_and_sources(monkeypatch):
    result = {
        "retrieved_chunks": [{"filename": "policy.pdf", "page": 2, "content": "Relevant"}],
        "sources": [{"filename": "policy.pdf", "page": 2, "excerpt": "Relevant"}],
    }
    monkeypatch.setattr(tools, "retrieve_context_with_trace", lambda question, filename: result)

    response = tools.search_knowledge("What is the policy?", filename="policy.pdf")

    assert response == {
        "question": "What is the policy?",
        "chunks": result["retrieved_chunks"],
        "sources": result["sources"],
    }


def test_ask_knowledge_uses_existing_rag_answer(monkeypatch):
    monkeypatch.setattr(
        tools,
        "ask_question",
        lambda question, filename=None: {"answer": "Answer", "sources": []},
    )

    assert tools.ask_knowledge("Question?", filename="policy.pdf") == {
        "answer": "Answer",
        "sources": [],
    }


@pytest.mark.parametrize("question", ["", "  ", "x" * (tools.MAX_QUESTION_LENGTH + 1)])
def test_knowledge_tools_reject_invalid_question(question):
    with pytest.raises(ValueError):
        tools.search_knowledge(question)


def test_list_documents_returns_chunk_counts(monkeypatch):
    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, statement):
            return SimpleNamespace(all=lambda: [("policy.pdf", 4)])

    monkeypatch.setattr(tools, "SessionLocal", FakeSession)

    assert tools.list_documents() == {
        "documents": [{"filename": "policy.pdf", "chunks": 4}]
    }
