from app.services.llm import generate_answer


context = """
The company uses Python, PostgreSQL, and FastAPI.
The project implements an enterprise AI document search system.
"""


question = "What technologies are used in the project?"


answer = generate_answer(
    context,
    question
)


print(answer)