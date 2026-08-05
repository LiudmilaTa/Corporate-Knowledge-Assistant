from app.services.embeddings import create_embedding
from app.services.search import search_documents
from app.services.llm import generate_answer

TOP_K = 5
def ask_question(question):

    # 1. Create an embedding for the question
    query_embedding = create_embedding(question)

    # 2. Search for similar documents
    results = search_documents(query_embedding)


    # 3. Assemble the context
    context_parts = []

    sources = []

    for row in results:
        filename, page, chunk_id, content, distance = row

        if len(context_parts) < TOP_K:
            context_parts.append(content)

    if {
        "filename": filename,
        "page": page
    } not in sources:

        sources.append(
            {
                "filename": filename,
                "page": page
            }
        )

    context = "\n\n".join(context_parts)


    # 4. Send the context to the LLM
    answer = generate_answer(
        context,
        question
    )


    return {
        "answer": answer,
        "sources": sources
    }