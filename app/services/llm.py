import requests


def generate_answer(context, question):

    prompt = f"""
You are a corporate AI assistant.
Respond only based on the provided context.
If the information is not in the context, say that there is insufficient data.

Context:
{context}

Question:
{question}

Answer:
"""


    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()
    
    return response.json()["response"]