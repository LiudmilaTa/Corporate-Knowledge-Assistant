from app.services.vector_db import save_document


fake_embedding = [0.1] * 384


save_document(
    filename="uploads/CV_Liudmila Taganashkina.pdf",
    page=1,
    chunk_id=0,
    content="This is a test document",
    embedding=fake_embedding
)


print("Document saved")