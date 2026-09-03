import re

from pgvector import Vector

from app.database import get_connection

SECTION_REFERENCE_PATTERN = re.compile(r"§\s*\d+[a-zA-Z]?", re.IGNORECASE)


def _section_references(question):
    return [reference.replace(" ", "") for reference in SECTION_REFERENCE_PATTERN.findall(question)]


def has_exact_section_reference(question, content):
    references = _section_references(question)
    normalized_content = re.sub(r"§\s*", "§", content, flags=re.IGNORECASE)
    return any(reference.casefold() in normalized_content.casefold() for reference in references)


def _query_terms(question):
    return [term for term in re.findall(r"[\wÀ-ž]+", question.casefold()) if len(term) >= 4]


def _lexical_score(content, terms):
    normalized_content = content.casefold()
    return sum(term in normalized_content for term in terms)


def search_documents(query_embedding, limit=5, filename=None, question=None):
    conn = get_connection()
    cur = conn.cursor()
    query_embedding = Vector(query_embedding)
    filename_filter = "WHERE filename = %s" if filename else ""
    parameters = (query_embedding, filename) if filename else (query_embedding,)

    cur.execute(
        f"""
        SELECT
            filename,
            page,
            chunk_id,
            content,
            embedding <=> %s AS distance
        FROM documents
        {filename_filter}
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        parameters + (query_embedding, max(limit * 5, 25)),
    )

    vector_results = cur.fetchall()
    lexical_results = []

    if question:
        section_references = _section_references(question)
        terms = _query_terms(question)
        if section_references or terms:
            lexical_filter = "WHERE "
            if filename:
                lexical_filter += "filename = %s AND "
            patterns = [
                rf"§\s*{reference[1:]}(?![A-Za-z0-9])"
                for reference in section_references
            ]
            patterns.extend(rf"\m{re.escape(term)}\M" for term in terms)
            lexical_filter += "(" + " OR ".join("content ~* %s" for _ in patterns) + ")"
            lexical_parameters = ((filename,) if filename else ()) + tuple(patterns)
            cur.execute(
                f"""
                SELECT
                    filename,
                    page,
                    chunk_id,
                    content,
                    embedding <=> %s AS distance
                FROM documents
                {lexical_filter}
                LIMIT %s
                """,
                (query_embedding,) + lexical_parameters + (max(limit * 20, 100),),
            )
            lexical_results = cur.fetchall()

    results_by_chunk = {
        (row[0], row[1], row[2]): row for row in vector_results + lexical_results
    }
    terms = _query_terms(question or "")
    results = sorted(
        results_by_chunk.values(),
        key=lambda row: (
            not has_exact_section_reference(question or "", row[3]),
            -_lexical_score(row[3], terms),
            row[4],
        ),
    )

    results = results[:limit]

    cur.close()
    conn.close()

    return results
