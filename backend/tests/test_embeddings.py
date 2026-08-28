import math

from app.services.embeddings import (
    embed_query,
    embed_texts,
)


EXPECTED_DIMENSION = 384


def test_embed_text_returns_correct_dimension() -> None:
    vectors = embed_texts(
        [
            "Database timeout caused by "
            "connection pool exhaustion."
        ]
    )

    assert len(vectors) == 1

    assert (
        len(vectors[0])
        == EXPECTED_DIMENSION
    )


def test_embed_multiple_texts() -> None:
    texts = [
        "Database timeout.",
        "Redis memory exhaustion.",
        "Authentication latency.",
    ]

    vectors = embed_texts(
        texts
    )

    assert len(vectors) == len(texts)

    for vector in vectors:
        assert (
            len(vector)
            == EXPECTED_DIMENSION
        )


def test_embeddings_are_normalized() -> None:
    vector = embed_texts(
        [
            "Database timeout."
        ]
    )[0]

    magnitude = math.sqrt(
        sum(
            value * value
            for value in vector
        )
    )

    assert abs(
        magnitude - 1.0
    ) < 0.001


def test_query_embedding_dimension() -> None:
    vector = embed_query(
        "Why are database requests timing out?"
    )

    assert (
        len(vector)
        == EXPECTED_DIMENSION
    )


def test_empty_query_is_rejected() -> None:
    try:
        embed_query("   ")

    except ValueError:
        return

    raise AssertionError(
        "Empty query should raise ValueError."
    )