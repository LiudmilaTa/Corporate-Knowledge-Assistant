# Project Structure

This document describes the repository layout and the responsibility of each important directory. The README remains intentionally focused on the product and the quickest way to run it.

## Repository map

```text
.
|-- app/
|   |-- api/                 HTTP routes and request handling
|   |-- core/                Cross-cutting application concerns
|   |-- db/                  SQLAlchemy base and session management
|   |-- models/              ORM models and Pydantic schemas
|   |-- services/            Ingestion, retrieval, embeddings, and LLM logic
|   |-- static/               CSS and browser-side JavaScript
|   |-- templates/            Jinja2 pages for the web interface
|   |-- database.py           Database compatibility helpers
|   `-- main.py               FastAPI application entry point
|-- alembic/
|   |-- versions/             Versioned database migrations
|   `-- env.py                Alembic runtime configuration
|-- docs/
|   |-- images/               Documentation and interface screenshots
|   |-- PROJECT_DETAILS.md    Architecture and implementation notes
|   `-- PROJECT_STRUCTURE.md  This repository map
|-- tests/                    Unit, integration, and API regression tests
|-- uploads/                  Local directory for uploaded PDF files
|-- docker-compose.yml        Local PostgreSQL and pgvector service
|-- pyproject.toml            Dependencies and project tooling
|-- ruff.toml                 Ruff linting configuration
|-- alembic.ini               Database migration configuration
|-- setup.bat                 Windows one-click setup
|-- setup.ps1                 PowerShell setup implementation
|-- start.bat                 Windows application launcher
`-- README.md                 Portfolio overview and quick start
```

## Application layers

### `app/main.py`

Creates the FastAPI application, mounts static assets, configures templates, and registers the routes.

### `app/api/`

Defines the HTTP contract for document management and chat interactions. This layer translates web requests into service calls and returns responses suitable for the UI.

### `app/services/`

Contains the domain workflow:

- `pdf_loader.py` extracts text while preserving page information.
- `splitter.py` turns extracted text into searchable chunks.
- `embeddings.py` creates multilingual vector representations.
- `vector_db.py` handles vector persistence and similarity queries.
- `search.py` combines semantic search with exact section matching.
- `rag.py` coordinates retrieval and context assembly.
- `llm.py` communicates with the local Ollama endpoint.
- `ingestion.py` orchestrates document processing from upload to storage.

### `app/models/` and `app/db/`

Define the persistence model, API schemas, SQLAlchemy metadata, and database session lifecycle. Alembic migrations keep the PostgreSQL schema reproducible.

### `app/templates/` and `app/static/`

Provide the user-facing chat and document management screens. Templates hold page structure; CSS and JavaScript provide layout, interactions, upload behavior, and chat updates.

### `tests/`

Verifies the system in small slices: parsing, splitting, ingestion, retrieval, LLM behavior, database integration, API routes, and model contracts.

## Request lifecycle

```text
PDF upload
  -> PDF extraction
  -> page-aware splitting
  -> multilingual embedding
  -> PostgreSQL + pgvector

Question
  -> optional multilingual query rewrite
  -> vector retrieval and exact-reference matching
  -> context selection
  -> Ollama answer generation
  -> answer and document sources
```