# Corporate Knowledge Assistant

## Overview

This project is a lightweight RAG application for searching and querying internal documents. The main goal is to let users upload PDF files, index their content, and ask questions using the most relevant retrieved chunks.

The core MVP is implemented and works locally with PostgreSQL, pgvector, and Ollama. The project is still in active development, with the current focus on reliability, evaluation, and the path from a local portfolio application to a deployable internal tool.

For the architecture, models, project status, tests, roadmap, and implementation notes, see [Project details](docs/PROJECT_DETAILS.md). The repository map is available in [Project structure](docs/PROJECT_STRUCTURE.md).

## Installation

Before starting the application, install Docker Desktop, `uv`. 

The setup script installs the Python dependencies and starts PostgreSQL, but it does not install Ollama or download models.

### One-click setup on Windows

From the project root, run:

```powershell
setup.bat
```

The script will:

- install Python requirements via `uv`
- create or reset the local `.venv`
- create a default `.env` if it is missing
- start PostgreSQL with Docker Compose
- run Alembic migrations
- show the command to launch the app

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
POSTGRES_CONNECT_TIMEOUT=5
HF_HUB_DISABLE_TELEMETRY=1
OLLAMA_MODEL=mistral
```

3. Install Ollama and download the local models as described in [Project details](docs/PROJECT_DETAILS.md#models-and-local-installation).

4. Start PostgreSQL and the app:

```bash
docker compose up -d
uv run uvicorn app.main:app --reload
```

5. Open the app at `http://localhost:8000`.

## License

This is proprietary software. The source code may be viewed, but use, copying, modification, and distribution require prior written permission from the copyright holder. See the [license terms](../LICENSE).