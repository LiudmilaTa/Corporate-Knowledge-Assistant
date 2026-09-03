import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


SECTION_PATTERN = re.compile(
    r"(?m)^§\s*\d+[a-zA-Z]?\b"
)


def split_text(text: str):
    sections = SECTION_PATTERN.split(text)
    headers = SECTION_PATTERN.findall(text)

    # Это обычный документ, без структуры § 1, § 2...
    if not headers:
        return splitter.split_text(text)

    chunks = []

    # Текст до первого §
    prefix = sections[0].strip()

    if prefix:
        chunks.extend(splitter.split_text(prefix))

    # Обрабатываем каждый § отдельно
    for header, section in zip(headers, sections[1:]):
        section_text = f"{header}\n{section.strip()}".strip()

        if not section_text:
            continue

        # Маленький параграф оставляем целиком.
        # Большой — дополнительно режем.
        if len(section_text) <= 1000:
            chunks.append(section_text)
            continue

        # Большой § режем отдельно
        section_chunks = splitter.split_text(section_text)

        for i, chunk in enumerate(section_chunks):
            # Каждый chunk большого § должен знать,
            # к какому § он относится.
            if not chunk.startswith(header):
                chunk = f"{header}\n{chunk}"

            chunks.append(chunk)       

    return chunks

def split_pages(pages):
    chunks = []

    current_section = None
    current_text = []
    current_page = None

    def save_current_section():
        if not current_section:
            return

        section_body = "\n".join(current_text).strip()
        section_text = f"{current_section}\n{section_body}".strip()

        if len(section_text) <= 1000:
            chunks.append({
                "page": current_page,
                "content": section_text,
            })
        else:
            for chunk in splitter.split_text(section_text):
                if not chunk.startswith(current_section):
                    chunk = f"{current_section}\n{chunk}"

                chunks.append({
                    "page": current_page,
                    "content": chunk,
                })

    for page in pages:
        text = page["text"]

        if not text:
            continue

        page_number = page["page"]

        sections = SECTION_PATTERN.split(text)
        headers = SECTION_PATTERN.findall(text)

        # На странице нет нового §
        if not headers:
            if current_section:
                current_text.append(text.strip())
            else:
                for chunk in splitter.split_text(text):
                    chunks.append({
                        "page": page_number,
                        "content": chunk,
                    })

            continue

        # Текст до первого §
        prefix = sections[0].strip()

        if prefix:
            if current_section:
                current_text.append(prefix)
            else:
                for chunk in splitter.split_text(prefix):
                    chunks.append({
                        "page": page_number,
                        "content": chunk,
                    })

        # Новые §
        for header, section in zip(headers, sections[1:]):

            # Закрываем предыдущий §
            if current_section:
                save_current_section()

            current_section = header
            current_page = page_number
            current_text = []

            if section.strip():
                current_text.append(section.strip())

    # Закрываем последний §
    save_current_section()

    return chunks