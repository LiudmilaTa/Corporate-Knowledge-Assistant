import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.core.logging import setup_logging
from app.services.embeddings import load_embedding_model

logger = logging.getLogger(__name__)


async def _initialize_embedding_model(app):
    try:
        await asyncio.to_thread(load_embedding_model)
    except Exception:
        logger.exception("Failed to load the embedding model")
        app.state.embedding_status = "error"
    else:
        app.state.embedding_status = "ready"


@asynccontextmanager
async def lifespan(app):
    app.state.embedding_status = "loading"
    model_task = asyncio.create_task(_initialize_embedding_model(app))
    yield
    if not model_task.done():
        model_task.cancel()


app = FastAPI(title="Corporate Knowledge Assistant", lifespan=lifespan)
app.state.embedding_status = "loading"
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
setup_logging()


@app.get("/health/ready", include_in_schema=False)
def readiness():
    return {"embedding_model": app.state.embedding_status}


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/documents-page", include_in_schema=False)
def documents_page(request: Request):
    return templates.TemplateResponse(request=request, name="documents.html", context={})
