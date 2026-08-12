from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    filename: Mapped[str | None] = mapped_column(
        Text,
    )

    page: Mapped[int | None] = mapped_column(
        Integer,
    )

    chunk_id: Mapped[int | None] = mapped_column(
        Integer,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
    )
