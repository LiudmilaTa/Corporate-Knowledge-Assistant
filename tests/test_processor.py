from app.services.pdf_loader import load_pdf
from app.services.document_processor import create_chunks


filename = "CV_Liudmila Taganashkina.pdf"


pages = load_pdf(
    f"uploads/{filename}"
)


chunks = create_chunks(
    pages,
    filename
)


print(
    "Total chunks:",
    len(chunks)
)


for chunk in chunks[:3]:

    print("\nTEXT:")
    print(
        chunk["text"][:300]
    )

    print("\nMETADATA:")
    print(
        chunk["metadata"]
    )