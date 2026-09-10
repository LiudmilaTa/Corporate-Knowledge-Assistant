from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
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
