from app.services.pdf_loader import load_pdf
from app.services.splitter import split_text


pages = load_pdf(
    "uploads/CV_Liudmila Taganashkina.pdf"
)


full_text = ""

for page in pages:
    full_text += page["text"]


chunks = split_text(full_text)


print("Total chunks:", len(chunks))


for i, chunk in enumerate(chunks[:3]):

    print("\n--- CHUNK", i+1, "---")
    print(chunk[:500])