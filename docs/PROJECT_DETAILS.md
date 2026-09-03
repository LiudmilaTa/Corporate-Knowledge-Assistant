# Corporate Knowledge Assistant

## Overview

This project is a lightweight RAG application for searching and querying internal documents. The main goal is to let users upload PDF files, index their content, and ask questions using the most relevant retrieved chunks.

## Architecture

The flow is simple:

1. User uploads a PDF document.
2. The document is parsed and split into text chunks.
3. Each chunk is embedded and stored in PostgreSQL with pgvector.
4. A user question is embedded and matched against stored chunks.
5. The most relevant chunks are passed to an LLM to produce an answer with source references.

## Main components

- FastAPI app for the web API and UI routes
- Document ingestion pipeline for PDF processing
- Embedding and vector search layer
- LLM integration for answer generation
- SQLAlchemy models and Alembic migrations for persistence

## Storage model

The core table stores document chunks together with their embeddings:

- filename
- page
- chunk_id
- content
- embedding

## Notes

The current implementation focuses on a simple, testable MVP. It is intentionally compact and suitable for local development and portfolio demonstration.