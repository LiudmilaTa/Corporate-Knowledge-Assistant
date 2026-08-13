from app.services.embeddings import create_embedding
from app.services.llm import generate_answer
from app.services.search import search_documents

TOP_K = 5
EXCERPT_LENGTH = 160

# cosine distance (0 = identical, 2 = opposite); results above this are treated as irrelevant
MAX_RELEVANT_DISTANCE = 0.6


class NoDocumentsIndexedError(Exception):
    """Raised when there are no documents in the vector store to search."""


class NoRelevantResultsError(Exception):
    """Raised when documents exist but none are relevant enough to the question."""

def ask_question(question):
    query_embedding = create_embedding(question)
    results = search_documents(query_embedding, limit=TOP_K)

    if not results:
        raise NoDocumentsIndexedError

    relevant_results = [row for row in results if row[4] <= MAX_RELEVANT_DISTANCE]

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
