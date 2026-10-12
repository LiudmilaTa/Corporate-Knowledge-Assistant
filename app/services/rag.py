from typing import Callable

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

    def __init__(self, search_candidates=None):
        super().__init__("No relevant results found")
        self.search_candidates = search_candidates or []


def ask_question_with_trace(
    question,
    filename=None,
    top_k=TOP_K,
    max_relevant_distance=MAX_RELEVANT_DISTANCE,
    progress_callback: Callable[[str], None] | None = None,
):
    def report_progress(message):
        if progress_callback:
            progress_callback(message)

    report_progress("embedding question")
    query_embedding = create_embedding(question)
    report_progress("searching vector index")
    if filename:
        results = search_documents(
            query_embedding,
            limit=top_k,
            filename=filename,
            question=question,
        )
    else:
        results = search_documents(query_embedding, limit=top_k, question=question)

    if not results:
        raise NoDocumentsIndexedError

    if filename:
        original_results = results
        report_progress("translating question to document language with Ollama")
        translated_question = translate_search_query(question, results[0][3])
        report_progress("embedding translated question")
        translated_embedding = create_embedding(translated_question)
        report_progress("searching translated question")
        translated_results = search_documents(
            translated_embedding,
            limit=top_k,
            filename=filename,
            question=translated_question,
        )
        if translated_results and min(row[4] for row in translated_results) < min(
            row[4] for row in original_results
        ):
            results = translated_results

    if not results:
        raise NoRelevantResultsError

    search_results = results
    relevant_results = [
        row
        for row in results
        if row[4] <= max_relevant_distance
        or has_exact_section_reference(question, row[3])
    ]

    if not relevant_results:
        raise NoRelevantResultsError(search_results)

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
    report_progress("generating answer with Ollama")
    answer = generate_answer(context, question)
    report_progress("answer generated")

    return {
        "answer": answer,
        "sources": sources,
        "context": context,
        "search_candidates": [
            {
                "filename": filename,
                "page": page,
                "chunk_id": chunk_id,
                "content": content,
                "distance": distance,
            }
            for filename, page, chunk_id, content, distance in search_results
        ],
        "retrieved_chunks": [
            {
                "filename": filename,
                "page": page,
                "chunk_id": chunk_id,
                "content": content,
                "distance": distance,
            }
            for filename, page, chunk_id, content, distance in relevant_results
        ],
    }


def ask_question(question, filename=None):
    result = ask_question_with_trace(question, filename=filename)
    return {"answer": result["answer"], "sources": result["sources"]}
