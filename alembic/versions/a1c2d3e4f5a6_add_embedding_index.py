"""add ivfflat index on documents embedding

Revision ID: a1c2d3e4f5a6
Revises: f6b62ddf19dd
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "f6b62ddf19dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ivfflat speeds up the `embedding <=> query` cosine distance search used by app/services/search.py
    op.execute(
        "CREATE INDEX IF NOT EXISTS documents_embedding_cosine_idx "
        "ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS documents_embedding_cosine_idx")
