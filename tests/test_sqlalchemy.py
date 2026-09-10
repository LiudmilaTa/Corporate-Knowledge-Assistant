from sqlalchemy import inspect

from app.db.session import engine


def test_database_connection():
    with engine.connect() as connection:
        assert connection.closed is False


def test_documents_table_exists():
    inspector = inspect(engine)

    assert inspector.has_table("documents")
