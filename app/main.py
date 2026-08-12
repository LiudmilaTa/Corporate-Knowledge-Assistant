from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.core.logging import setup_logging

app = FastAPI(title="Corporate Knowledge Assistant")
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
setup_logging()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/documents-page")
def documents_page(request: Request):
    return templates.TemplateResponse(request=request, name="documents.html", context={})
