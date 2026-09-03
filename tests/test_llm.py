from app.services.llm import generate_answer

def test_generate_answer_returns_string_for_valid_prompt():
    context = """
    The company uses Python, PostgreSQL, and FastAPI.
    The project implements an enterprise AI document search system.
    """
    question = "What technologies are used in the project?"

    answer = generate_answer(context, question)

    assert isinstance(answer, str)
    assert answer
