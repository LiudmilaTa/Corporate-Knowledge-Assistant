from sentence_transformers import SentenceTransformer

# multilingual model (also 384-dim) so cross-language questions (e.g. Russian question
# about a Czech document) still match relevant chunks by meaning, not just language
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def create_embedding(text: str):
    return model.encode(text).tolist()
