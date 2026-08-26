import json
from datetime import date
from pathlib import Path

from sqlalchemy import select

from app.db.models import Incident
from app.db.session import SessionLocal


DATA_FILE = Path("/data/sample_incidents/incidents.json")


def main() -> None:
    records = json.loads(
        DATA_FILE.read_text(encoding="utf-8")
    )

    inserted = 0
    skipped = 0

    with SessionLocal() as db:
        for item in records:
            existing = db.scalar(
                select(Incident).where(
                    Incident.incident_code == item["incident_code"]
                )
            )

            if existing is not None:
                skipped += 1
                continue

            incident = Incident(
                incident_code=item["incident_code"],
                title=item["title"],
                service=item["service"],
                severity=item["severity"],
                incident_date=date.fromisoformat(
                    item["incident_date"]
                ),
                symptoms=item["symptoms"],
                root_cause=item["root_cause"],
                solution=item["solution"],
                notes=item.get("notes"),
            )

            db.add(incident)
            inserted += 1

        db.commit()

    print(
        f"Seed complete: inserted={inserted}, skipped={skipped}"
    )


if __name__ == "__main__":
    main()