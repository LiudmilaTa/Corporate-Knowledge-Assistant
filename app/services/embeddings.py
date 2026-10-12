from threading import Lock

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# multilingual model (also 384-dim) so cross-language questions (e.g. Russian question
# about a Czech document) still match relevant chunks by meaning, not just language
_model = None
_model_lock = Lock()


def load_embedding_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer

                _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def is_embedding_model_loaded():
    return _model is not None


def create_embedding(text: str):
    return load_embedding_model().encode(text).tolist()
