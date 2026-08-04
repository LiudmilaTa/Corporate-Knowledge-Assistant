from app.services.ingestion import ingest_document


count = ingest_document(
    "uploads/CV_Liudmila Taganashkina.pdf",
    "CV_Liudmila Taganashkina.pdf"
)


print(
    f"Saved chunks: {count}"
)