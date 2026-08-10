# Corporate Knowledge Assistant

AI-powered corporate document search system based on RAG architecture.

The application allows users to upload internal documents, index their content, and search information using semantic similarity.

## Features (MVP)

* PDF document processing
* Text extraction
* Document chunking
* Vector embeddings generation
* Storage in PostgreSQL + pgvector
* Semantic similarity search
* Context retrieval
* Local LLM answer generation
* Source references in answers

## Architecture

User
|
v
FastAPI Web Application
|
v
Question Embedding
|
v
Vector Search (pgvector)
|
v
Relevant Document Chunks
|
v
Prompt Construction
|
v
Ollama + Mistral
|
v
Answer + Sources

## Tech Stack

Backend:

* Python 3.11
* FastAPI
* uv package manager

AI / ML:

* Sentence Transformers
* RAG architecture
* Ollama
* Mistral LLM

Database:

* PostgreSQL 16
* pgvector extension

Infrastructure:

* Docker
* Docker Compose

# Installation

## 1. Clone repository

```bash
git clone <repository-url>

cd Corporate-Knowledge-Assistant
```

## 2. Create environment

Install dependencies:

```bash
uv sync
```

## 3. Configure environment variables

Create `.env` file:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password

HF_HUB_DISABLE_TELEMETRY=1
```

## 4. Start PostgreSQL + pgvector with Docker

The project uses PostgreSQL with the pgvector extension for storing and searching document embeddings.

Make sure Docker Desktop is running.

Check Docker installation:

```bash
docker --version
```

Start database container:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

Expected output:

```
CONTAINER ID   IMAGE                    STATUS
xxxxx          pgvector/pgvector:pg16   Up
```
The database will be available at:

Host: localhost
Port: 5432
Database: rag_db
User: rag_user

#### Stop database

To stop containers:

```bash
docker compose down
```

#### Restart database

After restarting your computer:

```bash
docker compose up -d
```

#### View database logs

If there are connection problems:

```bash
docker compose logs postgres
```

## 5. Initialize pgvector database (first run only)

Connect to PostgreSQL container:

```bash
docker exec -it rag_postgres psql -U rag_user -d rag_db
```

Enable vector extension:

```sql
CREATE EXTENSION vector;
```

Create documents table:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    page INTEGER,
    chunk_id INTEGER,
    content TEXT,
    embedding vector(384)
);
```

Check table:

```sql
\dt
```

Exit:

```sql
\q
```

## 6. Run application

Start backend:

```bash
uv run uvicorn app.main:app --reload
```

Application:

```
http://localhost:8000
```

# Testing

Run PDF processing:

```bash
uv run python -m tests.test_ingestion
```

Test database connection:

```bash
uv run python -m tests.test_connection
```

Test vector search:

```bash
uv run python -m tests.test_search
```

# Project Documentation

Detailed architecture description:

[Project Details](docs/PROJECT_DETAILS.md)

## 7. Start Ollama

Install Ollama:

https://ollama.com


Download model:

```bash
ollama pull mistral
```

Run model:

```bash
ollama run mistral
```

## Screenshots

### Chat Interface

![Application screenshot](docs/images/chat.jpg)