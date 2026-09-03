import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.chat_message import ChatMessage
from app.models.document import Document
from app.models.schemas import DocumentResponse, QuestionRequest, QuestionResponse
from app.services.ingestion import ingest_document
from app.services.rag import NoDocumentsIndexedError, NoRelevantResultsError, ask_question

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    logger.info("Question received: %s", request.question)

    try:
        if request.filename:
            result = ask_question(request.question, filename=request.filename)
        else:
            result = ask_question(request.question)
        logger.info("RAG answer generated")

        with SessionLocal() as session:
            session.add(
                ChatMessage(
                    question=request.question,
                    answer=result["answer"],
                    sources=result.get("sources", []),
                )
            )
            session.commit()

        logger.info("Chat message saved")
        return result
    except RuntimeError as exc:
        logger.exception("Error while processing ask request: %s", exc)
        return {
            "answer": "Database is not available. Start PostgreSQL and try again.",
            "sources": [],
        }
    except NoDocumentsIndexedError:
        logger.warning("No documents indexed")
        return {
            "answer": "No documents indexed yet. Upload a PDF first.",
            "sources": [],
        }

    except NoRelevantResultsError:
        logger.warning("No relevant documents found for question")
        return {
            "answer": "No relevant information found in the indexed documents.",
            "sources": [],
        }

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename).name
    logger.info("Document upload started: %s", filename)
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    count = ingest_document(str(file_path), filename)

    logger.info("Document uploaded and indexed: %s (%s chunks)", filename, count)
    return {"filename": file.filename, "chunks": count}


@router.get("/documents", response_model=list[DocumentResponse])
def get_documents():
    with SessionLocal() as session:
        documents = session.execute(select(Document).order_by(Document.id)).scalars().all()
        return documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int):
    with SessionLocal() as session:
        document = session.get(Document, document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return document


@router.delete("/documents/{filename:path}")
def delete_document(filename: str):
    logger.info("Delete requested for document: %r", filename)

    with SessionLocal() as session:
        documents_to_delete = (
            session.execute(select(Document).where(Document.filename == filename))
            .scalars()
            .all()
        )

        if not documents_to_delete:
            logger.warning("Delete failed, no matching document: %r", filename)
            raise HTTPException(status_code=404, detail="Document not found")

        for document in documents_to_delete:
            session.delete(document)

        session.commit()
        logger.info("Deleted %s chunk(s) for document: %r", len(documents_to_delete), filename)
        return {
            "message": "Document deleted",
            "filename": filename,
            "deleted_count": len(documents_to_delete),
        }

@router.get("/chats")
def get_chat_history():
    with SessionLocal() as session:
        messages = session.query(ChatMessage).order_by(ChatMessage.created_at.desc()).all()
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


@router.delete("/chats/{message_id}")
def delete_chat_message(message_id: int):
    with SessionLocal() as session:
        message = session.get(ChatMessage, message_id)
        if message is None:
            raise HTTPException(status_code=404, detail="Chat message not found")

        session.delete(message)
        session.commit()
        return {"message": "Chat message deleted", "id": message_id}
