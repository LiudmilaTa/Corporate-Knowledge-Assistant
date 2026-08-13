from fastapi.testclient import TestClient

import app.api.routes as routes
from app.db.session import SessionLocal
from app.main import app
from app.models.chat_message import ChatMessage
from app.models.document import Document

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
                    "excerpt": "Test excerpt",
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


def test_delete_document_by_filename_removes_all_chunks():
    unique_filename = "delete-me-regression.pdf"

    with SessionLocal() as session:
        session.add_all(
            [
                Document(
                    filename=unique_filename,
                    page=1,
                    chunk_id=1,
                    content="chunk one",
                    embedding=[0.0] * 384,
                ),
                Document(
                    filename=unique_filename,
                    page=2,
                    chunk_id=2,
                    content="chunk two",
                    embedding=[0.0] * 384,
                ),
                Document(
                    filename="keep-me.pdf",
                    page=1,
                    chunk_id=1,
                    content="keep",
                    embedding=[0.0] * 384,
                ),
            ]
        )
        session.commit()

    response = client.delete(f"/documents/{unique_filename}")

    assert response.status_code == 200

    with SessionLocal() as session:
        deleted_rows = (
            session.query(Document)
            .filter(Document.filename == unique_filename)
            .all()
        )
        remaining_rows = (
            session.query(Document)
            .filter(Document.filename == "keep-me.pdf")
            .all()
        )

    assert deleted_rows == []
    assert any(row.filename == "keep-me.pdf" for row in remaining_rows)

    with SessionLocal() as session:
        session.query(Document).filter(Document.filename == "keep-me.pdf").delete()
        session.commit()
