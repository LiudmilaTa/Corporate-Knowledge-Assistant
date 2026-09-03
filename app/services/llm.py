import os

import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))


def translate_search_query(question, document_sample):
    prompt = f"""
Rewrite the question in the same language as the document sample below.
Return only the rewritten question, with no explanation.

Question:
{question}

Document sample:
{document_sample[:2000]}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0, "num_ctx": 4096},
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def generate_answer(context, question):
    prompt = f"""
You are a precise corporate knowledge assistant.
Answer the question using only the provided context.
Do not use general knowledge or invent facts.
If the context does not contain the answer, say: "Insufficient information in the provided documents."
Answer in the same language as the question.
Keep the answer concise and direct.

Context:
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
            },
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["response"]
