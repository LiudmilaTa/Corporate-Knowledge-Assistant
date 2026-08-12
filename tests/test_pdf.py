from app.services.pdf_loader import load_pdf


def test_load_pdf_returns_pages_with_text():
    pages = load_pdf("uploads/CV_Liudmila Taganashkina.pdf")

    assert isinstance(pages, list)
    assert pages
    assert all("page" in page and "text" in page for page in pages)
