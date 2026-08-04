from app.services.pdf_loader import load_pdf


pages = load_pdf(
    "uploads/CV_Liudmila Taganashkina.pdf"
)


for page in pages:
    print(
        "PAGE:",
        page["page"]
    )

    print(
        page["text"][:1500]
    )