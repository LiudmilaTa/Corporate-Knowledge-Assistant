from app.services.ingestion import ingest_document


def test_ingest_document_returns_integer_for_existing_pdf():
    count = ingest_document(
        "tests/fixtures/test.pdf",
        "test.pdf",
    )

    assert isinstance(count, int)
    assert count >= 0
