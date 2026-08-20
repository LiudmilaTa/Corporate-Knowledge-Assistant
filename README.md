# Corporate Knowledge Assistant

A small RAG-based assistant for searching and questioning company documents.

## What it does

- Uploads PDF documents
- Extracts text and splits it into chunks
- Creates embeddings and stores them in PostgreSQL + pgvector
- Answers questions using retrieved context and an LLM

## Tech stack

- Python 3.11
- FastAPI
- SQLAlchemy + PostgreSQL + pgvector
- Sentence Transformers
- pypdf + langchain text splitters
- uv

## Quick start

### One-click setup on Windows

From the project root, run:

```powershell
setup.bat
```

This script will:

- install Python requirements via `uv`
- create or reset the local `.venv`
- create a default `.env` if it is missing
- start PostgreSQL with Docker Compose
- run Alembic migrations
- show the command to launch the app

If `setup.bat` completed successfully, migrations have already been applied.

If you used the manual setup, run:

```powershell
uv run alembic upgrade head
```

Start the application:

```powershell
start.bat
```

Or:

```powershell
uv run uvicorn app.main:app --reload
```

Open the application at:

http://localhost:8000

#### LLM setup
The application uses Ollama with the mistral model.

Install Ollama from:

[Download Ollama](https://ollama.com/download)

Start Ollama and download the model:

```powershell
ollama pull mistral
```

The application expects Ollama at:

http://localhost:11434

#### PostgreSQL

PostgreSQL runs in Docker on port 5433.

Check its status:

```powershell
docker compose ps
```

Start it manually if needed:

```powershell
docker compose up -d --wait
```

Stop it with:

```powershell
docker compose down
```

#### Troubleshooting

If the application cannot connect to PostgreSQL, make sure Docker Desktop is running and that the container status is Healthy.

If answers cannot be generated, make sure Ollama is running and that the mistral model is installed.

### Manual setup

1. Install dependencies:

```bash
uv sync
```

2. Create a `.env` file with your database settings:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
HF_HUB_DISABLE_TELEMETRY=1
```

3. Start PostgreSQL:

```powershell
docker compose up -d --wait
```

4. Apply database migrations:

```powershell
uv run alembic upgrade head
```

5. Install Ollama from ollama.com, then download the required model:

```powershell
ollama pull mistral
```

Make sure Ollama is running and available at:

```text
http://localhost:11434
```

6. Start the application:

```powershell
uv run uvicorn app.main:app --reload
```

7. Open the app at:

```text
http://localhost:8000
```

## Testing

Run the main regression suite:

```bash
uv run pytest -q tests/test_rag.py tests/test_api.py tests/test_splitter.py tests/test_processor.py tests/test_ingestion.py tests/test_pdf.py tests/test_search.py tests/test_connection.py tests/test_db.py tests/test_llm.py tests/test_model.py
```

## Notes

- The app expects an LLM endpoint at `http://localhost:11434/api/generate` for answer generation.
- More detailed project context is available in [docs/PROJECT_DETAILS.md](docs/PROJECT_DETAILS.md).

### Chat Interface

![Application screenshot](docs/images/chat.jpg)