from app.services.embeddings import create_embedding
from app.services.pdf_loader import load_pdf
from app.services.splitter import split_text
from app.services.vector_db import save_document

def ingest_document(path, filename):
    pages = load_pdf(path)
    chunk_counter = 0

    for page in pages:
        page_number = page["page"]
        page_text = page["text"]

        if not page_text:
            continue

        for chunk in split_text(page_text):
            save_document(
                filename=filename,
                page=page_number,
                chunk_id=chunk_counter,
                content=chunk,
                embedding=create_embedding(chunk),
            )
            chunk_counter += 1

    return chunk_counter
