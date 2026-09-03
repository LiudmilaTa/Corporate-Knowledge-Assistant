from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    filename: str | None = None

class Source(BaseModel):
    filename: str
    page: int
    excerpt: str

class QuestionResponse(BaseModel):
    answer: str
    sources: list[Source]

class DocumentResponse(BaseModel):
    id: int
    filename: str | None
    page: int | None
    chunk_id: int | None
    content: str | None
