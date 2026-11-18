from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.rag import ask_question, retrieve_context_with_trace

MAX_QUESTION_LENGTH = 4000


def _validate_question(question: str) -> None:
    if not question.strip():
        raise ValueError("Question must not be empty")
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(f"Question must be at most {MAX_QUESTION_LENGTH} characters")


def search_knowledge(question: str, filename: str | None = None) -> dict:
    """Search indexed documents and return relevant passages with source details."""
    _validate_question(question)
    result = retrieve_context_with_trace(question, filename=filename)
    return {
        "question": question,
        "chunks": result["retrieved_chunks"],
        "sources": result["sources"],
    }


def ask_knowledge(question: str, filename: str | None = None) -> dict:
    """Answer from indexed documents and include document/page citations."""
    _validate_question(question)
    return ask_question(question, filename=filename)


def list_documents() -> dict:
    """List indexed PDF filenames and their number of indexed chunks."""
    statement = (
        select(Document.filename, func.count(Document.id).label("chunk_count"))
        .where(Document.filename.is_not(None))
        .group_by(Document.filename)
        .order_by(Document.filename)
    )
    with SessionLocal() as session:
        documents = session.execute(statement).all()

    return {
        "documents": [
            {"filename": filename, "chunks": chunk_count}
            for filename, chunk_count in documents
        ]
    }
