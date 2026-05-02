"""
Embedding Generation using Sentence-Transformers (BERT-based).
Uses 'all-MiniLM-L6-v2' — 384-dimensional embeddings.
"""
from typing import List
import numpy as np

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embedding(text: str) -> List[float]:
    model = get_embedding_model()
    embedding = model.encode(text[:5000], normalize_embeddings=True)
    return embedding.tolist()

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode([t[:5000] for t in texts], normalize_embeddings=True, batch_size=32)
    return [e.tolist() for e in embeddings]

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    a, b = np.array(vec_a), np.array(vec_b)
    return max(0.0, min(1.0, float(np.dot(a, b))))
