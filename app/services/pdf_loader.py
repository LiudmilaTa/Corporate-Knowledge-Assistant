from pypdf import PdfReader


def load_pdf(path):

    reader = PdfReader(path)

    pages = []

    for number, page in enumerate(reader.pages):

        text = page.extract_text()

        pages.append(
            {
                "page": number + 1,
                "text": text
            }
        )

    return pages