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
     try:
         return ask_question(request.question)
     except UnboundLocalError:
         return {
             "answer": "No documents indexed yet. Upload a PDF first.",
             "sources": [],
         }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

     filename = Path(file.filename).name
     file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
         while chunk := await file.read(1024 * 1024):
             buffer.write(chunk)

     count = ingest_document(str(file_path), filename)

    return {
        "filename": file.filename,
        "chunks": count
    }