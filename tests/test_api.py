from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.chat_message import ChatMessage

import app.api.routes as routes


client = TestClient(app)


def test_get_documents():
    response = client.get("/documents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_chat_history():
    response = client.get("/chats")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_missing_document():
    response = client.get("/documents/999999")

    assert response.status_code == 404


def test_ask_saves_chat_message(monkeypatch):
    def fake_ask_question(question):
        return {
            "answer": "Test answer",
            "sources": [
                {
                    "filename": "test.pdf",
                    "page": 1,
                }
            ],
        }

    monkeypatch.setattr(
        routes,
        "ask_question",
        fake_ask_question,
    )

    question = "What is this document about?"

    response = client.post(
        "/ask",
        json={"question": question},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Test answer"
    assert data["sources"][0]["filename"] == "test.pdf"

    with SessionLocal() as session:
        message = (
            session.query(ChatMessage)
            .filter(ChatMessage.question == question)
            .order_by(ChatMessage.id.desc())
            .first()
        )

        assert message is not None
        assert message.answer == "Test answer"

def test_upload_document(monkeypatch):
    def fake_ingest_document(file_path, filename):
        return 3

    monkeypatch.setattr(
        routes,
        "ingest_document",
        fake_ingest_document,
    )

    response = client.post(
        "/upload",
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert data["chunks"] == 3