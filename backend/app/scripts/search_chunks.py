import argparse

from app.db.session import SessionLocal
from app.services.retrieval import (
    search_chunks,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Search document chunks using "
            "pgvector cosine similarity."
        )
    )

    parser.add_argument(
        "query",
        type=str,
        help="Natural-language search query.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return.",
    )

    parser.add_argument(
        "--service",
        type=str,
        default=None,
        help="Optional service filter.",
    )

    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help="Optional section filter.",
    )

    args = parser.parse_args()

    with SessionLocal() as db:
        results = search_chunks(
            db,
            args.query,
            top_k=args.top_k,
            service=args.service,
            section=args.section,
        )

    if not results:
        print(
            "No matching chunks found."
        )
        return

    print()
    print(
        f"Query: {args.query}"
    )
    print(
        f"Results: {len(results)}"
    )
    print()

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            "=" * 70
        )

        print(
            f"Rank: {rank}"
        )

        print(
            f"Similarity: "
            f"{result.similarity:.4f}"
        )

        print(
            f"Document: "
            f"{result.document_title}"
        )

        print(
            f"Filename: "
            f"{result.original_filename}"
        )

        print(
            f"Section: "
            f"{result.section}"
        )

        print(
            f"Service: "
            f"{result.service}"
        )

        print(
            f"Severity: "
            f"{result.severity}"
        )

        print(
            f"Incident Date: "
            f"{result.incident_date}"
        )

        print()
        print(
            "Text:"
        )
        print(
            result.text
        )
        print()


if __name__ == "__main__":
    main()