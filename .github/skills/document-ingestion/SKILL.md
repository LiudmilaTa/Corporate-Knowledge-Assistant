---
name: document-ingestion
description: Change PDF parsing, chunking, embedding, or document indexing safely.
---

# Document ingestion

Use this Skill when modifying PDF ingestion or the indexed document representation.

- Preserve page metadata through extraction, splitting, embedding, and persistence.
- Check the existing pipeline in `app/services/pdf_loader.py`, `splitter.py`, `embeddings.py`, and `ingestion.py` before introducing helpers.
- If embedding dimensions or persisted fields change, update the SQLAlchemy model and Alembic migration and document the re-indexing requirement.
- Add tests for the relevant stage; run `uv run pytest -q tests/test_pdf.py tests/test_splitter.py tests/test_ingestion.py`.
- Do not silently skip malformed documents or report a successful index when ingestion fails.
