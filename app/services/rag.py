from app.services.embeddings import create_embedding
from app.services.llm import generate_answer, translate_search_query
from app.services.search import has_exact_section_reference, search_documents

TOP_K = 5
EXCERPT_LENGTH = 160

# cosine distance (0 = identical, 2 = opposite); results above this are treated as irrelevant
MAX_RELEVANT_DISTANCE = 0.6


class NoDocumentsIndexedError(Exception):
    """Raised when there are no documents in the vector store to search."""


class NoRelevantResultsError(Exception):
    """Raised when documents exist but none are relevant enough to the question."""

def ask_question(question, filename=None):
    query_embedding = create_embedding(question)
    if filename:
        results = search_documents(
            query_embedding,
            limit=TOP_K,
            filename=filename,
            question=question,
        )
    else:
        results = search_documents(query_embedding, limit=TOP_K, question=question)

    if not results:
        raise NoDocumentsIndexedError

    if filename:
        original_results = results
        translated_question = translate_search_query(question, results[0][3])
        translated_embedding = create_embedding(translated_question)
        translated_results = search_documents(
            translated_embedding,
            limit=TOP_K,
            filename=filename,
            question=translated_question,
        )
        if translated_results and min(row[4] for row in translated_results) < min(
            row[4] for row in original_results
        ):
            results = translated_results

    if not results:
        raise NoRelevantResultsError

    relevant_results = [
        row
        for row in results
        if row[4] <= MAX_RELEVANT_DISTANCE
        or has_exact_section_reference(question, row[3])
    ]

    if not relevant_results:
        raise NoRelevantResultsError

    context_parts = []
    sources = []
    seen_sources = set()

    for filename, page, chunk_id, content, distance in relevant_results:
        context_parts.append(content)

        source_key = (filename, page)
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            excerpt = content.strip().replace("\n", " ")
            if len(excerpt) > EXCERPT_LENGTH:
                excerpt = excerpt[:EXCERPT_LENGTH].rsplit(" ", 1)[0] + "…"
            sources.append({"filename": filename, "page": page, "excerpt": excerpt})

    context = "\n\n".join(context_parts)
    answer = generate_answer(context, question)

    return {
        "answer": answer,
        "sources": sources,
    }
