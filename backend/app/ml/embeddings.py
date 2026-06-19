"""
Lightweight Embedding Generation using Skill Taxonomy Vectorization.
Creates normalized feature vectors based on skill occurrences to calculate cosine similarity.
"""
import re
import numpy as np
from typing import List
from app.ml.ner import SKILL_TAXONOMY

# Create a deterministic vocabulary from the sorted skill taxonomy
_vocab = sorted(list(SKILL_TAXONOMY))

def generate_embedding(text: str) -> List[float]:
    """
    Generate a normalized binary embedding vector for the text based on skill occurrences.
    """
    text_lower = text.lower()
    vector = []
    
    for skill in _vocab:
        # Use word boundaries for short skill names (3 chars or less) to avoid false matches
        if len(skill) <= 3:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                vector.append(1.0)
            else:
                vector.append(0.0)
        else:
            if skill in text_lower:
                vector.append(1.0)
            else:
                vector.append(0.0)
                
    # Normalize the vector to unit length
    arr = np.array(vector)
    norm = np.linalg.norm(arr)
    if norm > 0:
        arr = arr / norm
    return arr.tolist()

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embedding vectors for a batch of texts.
    """
    return [generate_embedding(t) for t in texts]

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity between two normalized vectors (dot product).
    """
    a, b = np.array(vec_a), np.array(vec_b)
    # Since the vectors are pre-normalized to unit length, cosine similarity is just the dot product
    dot_val = float(np.dot(a, b))
    return max(0.0, min(1.0, dot_val))
