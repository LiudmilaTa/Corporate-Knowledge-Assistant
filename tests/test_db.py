from app.db.session import SessionLocal
from app.models.document import Document
from app.services.vector_db import save_document

def test_save_document_accepts_embedding_payload():
    fake_embedding = [0.1] * 384

    save_document(
        filename="test.pdf",
        page=1,
        chunk_id=0,
        content="This is a test document",
        embedding=fake_embedding,
    )

    with SessionLocal() as session:
        session.query(Document).filter(Document.filename == "test.pdf").delete()
        session.commit()
