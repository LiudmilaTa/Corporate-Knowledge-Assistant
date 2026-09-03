from app.services.embeddings import create_embedding
from app.services.search import search_documents

def test_search_documents_returns_list_of_results():
    question = "What skills are listed in the document?"
    query_vector = create_embedding(question)
    results = search_documents(query_vector)

    assert isinstance(results, list)
    assert all(len(item) >= 5 for item in results)
