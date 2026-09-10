from app.services.embeddings import create_embedding
from app.services.pdf_loader import load_pdf
from app.services.splitter import split_pages
from app.services.vector_db import replace_document


def ingest_document(path, filename):
    pages = load_pdf(path)
    chunks = split_pages(pages)

    indexed_chunks = []
    for chunk in chunks:
        indexed_chunks.append(
            {
                **chunk,
                "embedding": create_embedding(chunk["content"]),
            }
        )

    replace_document(filename, indexed_chunks)

    return len(chunks)
