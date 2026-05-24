"""Embedding service for RAG."""
from sentence_transformers import SentenceTransformer
import numpy as np

# Global model instance (lazy loading)
_model = None


def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model singleton."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector for text."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts."""
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings.tolist()


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2))


def vector_to_sql(vec: list[float]) -> str:
    """Convert Python list to PostgreSQL vector string format."""
    return '[' + ','.join(str(x) for x in vec) + ']'