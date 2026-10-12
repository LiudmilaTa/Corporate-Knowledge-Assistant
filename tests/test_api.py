from threading import Event

import psycopg
from fastapi.testclient import TestClient

import app.api.routes as routes
import app.main as main_module
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
    monkeypatch.setattr(routes, "is_embedding_model_loaded", lambda: True)

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

def test_ask_returns_service_message_when_database_is_unavailable(monkeypatch):
    monkeypatch.setattr(routes, "is_embedding_model_loaded", lambda: True)

    def fake_ask_question(question):
        raise psycopg.Error("connection timeout expired")

    monkeypatch.setattr(routes, "ask_question", fake_ask_question)

    response = client.post(
        "/ask",
        json={"question": "What is this document about?"},
    )

    assert response.status_code == 200
    assert "Database is not available" in response.json()["answer"]


def test_upload_document(monkeypatch):
    monkeypatch.setattr(routes, "is_embedding_model_loaded", lambda: True)

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


def test_readiness_reports_embedding_model_status():
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["embedding_model"] in {"loading", "ready", "error"}


def test_homepage_is_available_during_model_loading(monkeypatch):
    model_loading_started = Event()
    allow_model_loading_to_finish = Event()

    def delayed_model_load():
        model_loading_started.set()
        if not allow_model_loading_to_finish.wait(timeout=5):
            raise TimeoutError("Test did not release the embedding model loader")

    monkeypatch.setattr(main_module, "load_embedding_model", delayed_model_load)

    try:
        with TestClient(app) as startup_client:
            assert model_loading_started.wait(timeout=2)
            readiness = startup_client.get("/health/ready")
            response = startup_client.get("/")

            assert readiness.json()["embedding_model"] == "loading"
            assert response.status_code == 200
            assert "Loading the AI embedding model" in response.text
    finally:
        allow_model_loading_to_finish.set()


def test_ask_returns_service_unavailable_while_model_loads(monkeypatch):
    monkeypatch.setattr(routes, "is_embedding_model_loaded", lambda: False)

    response = client.post("/ask", json={"question": "What is this document about?"})

    assert response.status_code == 503
    assert "still loading" in response.json()["detail"]


def test_upload_rejects_non_pdf():
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"not a PDF", "text/plain")},
    )

    assert response.status_code == 415


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 422


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
