from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.models.schemas import QuestionRequest, QuestionResponse
from app.services.ingestion import ingest_document
from app.services.rag import ask_question

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.schemas import DocumentResponse
from app.models.chat_message import ChatMessage

import logging

router = APIRouter()

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post(
    "/ask",
    response_model=QuestionResponse,
)
def ask(request: QuestionRequest):
    logger.info("Question received: %s", request.question)

    try:
        result = ask_question(request.question)

        logger.info("RAG answer generated")

        with SessionLocal() as session:
            chat_message = ChatMessage(
                question=request.question,
                answer=result["answer"],
                sources=result.get("sources", []),
            )

            session.add(chat_message)
            session.commit()

        logger.info("Chat message saved")
        return result

    except UnboundLocalError:
        logger.warning("No documents indexed")
        return {
            "answer": "No documents indexed yet. Upload a PDF first.",
            "sources": [],
        }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    filename = Path(file.filename).name
    logger.info("Document upload started: %s", filename)
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    count = ingest_document(
        str(file_path),
        filename,
    )

    logger.info(
        "Document uploaded and indexed: %s (%s chunks)",
        filename,
        count,
    )
    
    return {
        "filename": file.filename,
        "chunks": count,
    }

@router.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def get_documents():
    with SessionLocal() as session:
        result = session.execute(
            select(Document).order_by(Document.id)
        )

        documents = result.scalars().all()

        return documents

@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(document_id: int):
    with SessionLocal() as session:
        document = session.get(Document, document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        return document

@router.delete("/documents/{document_id}")
def delete_document(document_id: int):
    with SessionLocal() as session:
        document = session.get(Document, document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        session.delete(document)
        session.commit()

        return {
            "message": "Document deleted",
            "id": document_id,
        }

@router.get("/chats")
def get_chat_history():
    with SessionLocal() as session:
        messages = (
            session.query(ChatMessage)
            .order_by(ChatMessage.created_at.desc())
            .all()
        )

        return [
            {
                "id": message.id,
                "question": message.question,
                "answer": message.answer,
                "sources": message.sources,
                "created_at": message.created_at,
            }
            for message in messages
        ]