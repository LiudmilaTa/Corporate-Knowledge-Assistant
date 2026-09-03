from app.services.embeddings import create_embedding
from app.services.pdf_loader import load_pdf
from app.services.splitter import split_pages
from app.services.vector_db import save_document


def ingest_document(path, filename):
    pages = load_pdf(path)
    chunks = split_pages(pages)

    for chunk_id, chunk in enumerate(chunks):
        content = chunk["content"]

        save_document(
            filename=filename,
            page=chunk["page"],
            chunk_id=chunk_id,
            content=content,
            embedding=create_embedding(content),
        )

    return len(chunks)