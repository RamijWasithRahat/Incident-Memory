from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


QUERY_PREFIX = (
    "Represent this sentence for searching relevant passages: "
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    The model is cached in memory after the first call.
    """
    return SentenceTransformer(
        settings.embedding_model
    )


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    """
    Convert document/chunk texts into normalized
    embedding vectors.
    """

    if not texts:
        return []

    cleaned_texts = [
        text.strip()
        for text in texts
        if text.strip()
    ]

    if not cleaned_texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return [
        vector.tolist()
        for vector in embeddings
    ]


def embed_query(
    query: str,
) -> list[float]:
    """
    Convert a user's search query into a normalized
    embedding vector.
    """

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError(
            "Query must not be empty."
        )

    model = get_embedding_model()

    embedding = model.encode(
        QUERY_PREFIX + cleaned_query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embedding.tolist()