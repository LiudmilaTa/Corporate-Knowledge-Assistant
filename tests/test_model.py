from app.models.document import Document


def test_document_table_name():
    assert Document.__tablename__ == "documents"


def test_document_columns():
    columns = set(Document.__table__.columns.keys())

    assert columns == {
        "id",
        "filename",
        "page",
        "chunk_id",
        "content",
        "embedding",
    }
