from app.services.ingestion import ingest_document

def test_ingest_document_returns_integer_for_existing_pdf():
    count = ingest_document(
        "uploads/CV_Liudmila Taganashkina.pdf",
        "CV_Liudmila Taganashkina.pdf",
    )

    assert isinstance(count, int)
    assert count >= 0
