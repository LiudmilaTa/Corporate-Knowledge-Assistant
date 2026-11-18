# AI context: project overview

Corporate Knowledge Assistant is a local-first RAG application for asking questions about uploaded corporate PDFs. The web application is built with FastAPI; PostgreSQL with pgvector stores page-aware chunks and embeddings; Sentence Transformers creates multilingual embeddings; Ollama rewrites selected queries and generates grounded answers.

The project is an actively developed portfolio MVP, not a production-ready multi-user service. It currently has no authentication or document-level authorization.

## Main paths

- `app/api/`: web endpoints and request validation.
- `app/services/`: PDF ingestion, embeddings, retrieval, and LLM integration.
- `app/mcp/`: local, read-only MCP tools that reuse the RAG services.
- `app/models/`, `app/db/`, `alembic/`: persistence models, sessions, and migrations.
- `tests/`: unit, service, and integration tests.
- `evals/` and `docs/RAG_EVALUATION.md`: evaluation dataset, workflow, and results.

## Product and AI-assistant context

The chat history is a record of independent questions and answers. It is not yet a multi-turn conversational memory and must not be described as one. The repository's AI memory bank is the documentation in this directory; it is for coding assistants, not user data.
