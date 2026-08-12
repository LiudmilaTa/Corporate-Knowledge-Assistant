from app.services.embeddings import create_embedding
from app.services.llm import generate_answer
from app.services.search import search_documents

TOP_K = 5

def ask_question(question):
    query_embedding = create_embedding(question)
    results = search_documents(query_embedding, limit=TOP_K)

    context_parts = []
    sources = []

    for filename, page, chunk_id, content, distance in results:
        context_parts.append(content)
        sources.append({"filename": filename, "page": page})

    context = "\n\n".join(context_parts)
    answer = generate_answer(context, question)

    return {
        "answer": answer,
        "sources": sources,
    }
