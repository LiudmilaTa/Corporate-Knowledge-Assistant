from app.services.embeddings import create_embedding
from app.services.search import has_exact_section_reference, search_documents


def test_exact_section_reference_does_not_match_a_longer_section_number():
    question = "What does § 1 regulate?"

    assert has_exact_section_reference(question, "§ 1 Subject matter")
    assert not has_exact_section_reference(question, "§ 10 Other provisions")
    assert not has_exact_section_reference(question, "§ 175 Final provisions")
    assert not has_exact_section_reference(question, "§ 1a Special provisions")


def test_search_documents_returns_list_of_results():
    question = "What skills are listed in the document?"
    query_vector = create_embedding(question)
    results = search_documents(query_vector)

    assert isinstance(results, list)
    assert all(len(item) >= 5 for item in results)
