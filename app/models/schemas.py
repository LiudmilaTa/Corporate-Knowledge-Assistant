from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class Source(BaseModel):
    filename: str
    page: int


class QuestionResponse(BaseModel):
    answer: str
    sources: list[Source]