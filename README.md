# Corporate Knowledge Assistant

## Overview

This project is a lightweight RAG application for searching and querying internal documents. The main goal is to let users upload PDF files, index their content, and ask questions using the most relevant retrieved chunks.

The core MVP is implemented and works locally with PostgreSQL, pgvector, and Ollama. The project is still in active development, with the current focus on reliability, evaluation, and the path from a local portfolio application to a deployable internal tool.

For the architecture, models, project status, tests, roadmap, and implementation notes, see [Project details](docs/PROJECT_DETAILS.md). The repository map is available in [Project structure](docs/PROJECT_STRUCTURE.md).
The local RAG evaluation methodology, results, and improvement plan are documented in [RAG evaluation](docs/RAG_EVALUATION.md).
The local read-only MCP server and AI coding context are described in [Project details](docs/PROJECT_DETAILS.md#mcp-and-ai-development-context).

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
POSTGRES_PORT=5434
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

## MCP integration

The repository includes a local, read-only MCP server for indexed knowledge. Configure the project in VS Code, start PostgreSQL, apply migrations, and ensure the embedding model and Ollama are available before using search and answer tools. The MCP server can be started directly with:

```powershell
uv run python -m app.mcp.server
```

VS Code's workspace MCP configuration is in `.vscode/mcp.json`. The server exposes `search_knowledge`, `ask_knowledge`, and `list_documents` over stdio; it does not expose upload or delete operations. See [MCP and AI development context](docs/PROJECT_DETAILS.md#mcp-and-ai-development-context) for setup and limitations.

## License

This is proprietary software. The source code may be viewed, but use, copying, modification, and distribution require prior written permission from the copyright holder. See the [license terms](../LICENSE).