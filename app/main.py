from fastapi import FastAPI
from app.api.upload import router as upload_router


app = FastAPI(
    title="Corporate AI Search"
)

app.include_router(
    upload_router
)

@app.get("/")
def home():
    return {
        "message": "RAG MVP is running"
    }