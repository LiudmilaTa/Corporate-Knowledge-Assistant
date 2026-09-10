from app.services.splitter import split_pages, split_text


def test_small_text_stays_in_one_chunk():
    text = "§ 1\nPředmět úpravy\n(1) Tento zákon upravuje podmínky."

    chunks = split_text(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_law_sections_are_preserved():
    text = """§ 1
Předmět úpravy

(1) Tento zákon upravuje podmínky vstupu cizince.

§ 2
Působnost zákona

Tento zákon se nevztahuje na některé osoby.
"""

    chunks = split_text(text)

    assert len(chunks) == 2

    assert "§ 1" in chunks[0]
    assert "Předmět úpravy" in chunks[0]
    assert "§ 2" in chunks[1]
    assert "Působnost zákona" in chunks[1]


def test_sections_are_not_mixed():
    text = """§ 1
První paragraf.

§ 2
Druhý paragraf.
"""

    chunks = split_text(text)

    assert not (
        "§ 1" in chunks[0]
        and "§ 2" in chunks[0]
    )


def test_large_section_can_be_split():
    text = """§ 1
""" + ("Tento text obsahuje informace o pobytu cizinců. " * 100)

    chunks = split_text(text)

    assert len(chunks) > 1


def test_large_section_keeps_section_header():
    text = """§ 1
    """ + ("Tento zákon upravuje podmínky pobytu cizince. " * 100)

    chunks = split_text(text)

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk.startswith("§ 1")


def test_split_pages_preserves_page_number():
    pages = [
        {
            "page": 1,
            "text": "Первый текст.",
        },
        {
            "page": 2,
            "text": "Второй текст.",
        },
    ]

    chunks = split_pages(pages)

    assert len(chunks) == 2
    assert chunks[0]["page"] == 1
    assert chunks[1]["page"] == 2

def test_section_can_continue_on_next_page():
    pages = [
        {
            "page": 1,
            "text": """§ 1
Předmět úpravy

(1) Tento zákon upravuje podmínky vstupu cizince.
Pokračování věty""",
        },
        {
            "page": 2,
            "text": """pokračuje na další stránce.

Další text stejného paragrafu.

§ 2
Působnost zákona

Tento zákon se nevztahuje na některé osoby.
""",
        },
    ]

    chunks = split_pages(pages)

    assert any("§ 1" in chunk["content"] for chunk in chunks)
    assert any("Pokračování věty" in chunk["content"] for chunk in chunks)
    assert any("pokračuje na další stránce" in chunk["content"] for chunk in chunks)
    assert any("§ 2" in chunk["content"] for chunk in chunks)
