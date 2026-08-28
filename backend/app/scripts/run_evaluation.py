from app.db.session import SessionLocal
from app.services.evaluation import (
    run_retrieval_evaluation,
)


def main() -> None:
    print(
        "Incident Memory "
        "M8 Retrieval Evaluation"
    )

    print(
        "=" * 60
    )

    with SessionLocal() as db:
        summary = (
            run_retrieval_evaluation(
                db,
                top_k=3,
            )
        )

    print()

    print(
        f"Metric: "
        f"{summary.metric}"
    )

    print(
        f"Questions: "
        f"{summary.total_questions}"
    )

    print(
        f"Passed: "
        f"{summary.passed_questions}"
    )

    print(
        f"Failed: "
        f"{summary.failed_questions}"
    )

    print(
        f"Top-3 Retrieval Success: "
        f"{summary.score_percent:.2f}%"
    )

    print(
        f"Average Retrieval Time: "
        f"{summary.average_retrieval_ms:.2f} ms"
    )

    failed = [
        result
        for result in summary.results
        if not result.passed
    ]

    if failed:
        print()
        print(
            "Failed Questions"
        )
        print(
            "-" * 60
        )

        for result in failed:
            print()
            print(
                f"{result.question_id}: "
                f"{result.question}"
            )

            print(
                "Expected:"
            )

            for expected in (
                result.expected_sources
            ):
                print(
                    f"  - {expected}"
                )

            print(
                "Retrieved:"
            )

            if (
                not
                result.retrieved_sources
            ):
                print(
                    "  - No results"
                )

            for source in (
                result.retrieved_sources
            ):
                source_name = (
                    source.incident_code
                    or source.document_title
                )

                print(
                    f"  {source.rank}. "
                    f"{source_name} / "
                    f"{source.section} "
                    f"({source.similarity:.4f})"
                )

    print()
    print(
        "Reports written to:"
    )

    print(
        "/data/evaluation/results/"
        "latest.json"
    )

    print(
        "/data/evaluation/results/"
        "latest.csv"
    )


if __name__ == "__main__":
    main()