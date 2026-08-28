import json
from datetime import date
from pathlib import Path

from sqlalchemy import select

from app.db.models import Incident
from app.db.session import SessionLocal
from app.services.incident_indexing import (
    index_incident,
)


DATA_FILE = Path(
    "/data/sample_incidents/incidents.json"
)


def main() -> None:
    records = json.loads(
        DATA_FILE.read_text(
            encoding="utf-8"
        )
    )

    inserted = 0
    skipped = 0
    indexed = 0

    with SessionLocal() as db:
        try:
            for item in records:
                incident = db.scalar(
                    select(
                        Incident
                    ).where(
                        Incident.incident_code
                        == item["incident_code"]
                    )
                )

                if incident is None:
                    incident = Incident(
                        incident_code=(
                            item["incident_code"]
                        ),
                        title=item["title"],
                        service=item["service"],
                        severity=item["severity"],
                        incident_date=(
                            date.fromisoformat(
                                item[
                                    "incident_date"
                                ]
                            )
                        ),
                        symptoms=item[
                            "symptoms"
                        ],
                        root_cause=item[
                            "root_cause"
                        ],
                        solution=item[
                            "solution"
                        ],
                        notes=item.get(
                            "notes"
                        ),
                    )

                    db.add(incident)
                    db.flush()

                    inserted += 1

                else:
                    skipped += 1

                index_incident(
                    db,
                    incident,
                )

                indexed += 1

            db.commit()

        except Exception:
            db.rollback()
            raise

    print(
        "Seed complete: "
        f"inserted={inserted}, "
        f"skipped={skipped}, "
        f"indexed={indexed}"
    )


if __name__ == "__main__":
    main()