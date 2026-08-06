from fastapi import APIRouter
from fastapi import UploadFile, File
from pathlib import Path

from app.models.schemas import (
    QuestionRequest,
    QuestionResponse,
)

from app.services.rag import ask_question
from app.services.ingestion import ingest_document

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post(
    "/ask",
    response_model=QuestionResponse,
)
def ask(request: QuestionRequest):

    result = ask_question(request.question)

    return result

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    count = ingest_document(
        str(file_path)
    )

    return {
        "filename": file.filename,
        "chunks": count
    }