from sqlalchemy import select

from app.db.models import Incident
from app.db.session import SessionLocal
from app.services.incident_indexing import (
    index_incident,
)


def main() -> None:
    with SessionLocal() as db:
        incidents = list(
            db.scalars(
                select(
                    Incident
                ).order_by(
                    Incident.id
                )
            ).all()
        )

        if not incidents:
            print(
                "No incidents found."
            )
            return

        print(
            f"Found {len(incidents)} incidents."
        )

        try:
            for number, incident in enumerate(
                incidents,
                start=1,
            ):
                index_incident(
                    db,
                    incident,
                )

                print(
                    f"[{number}/{len(incidents)}] "
                    f"Indexed "
                    f"{incident.incident_code}"
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

        print(
            "Incident reindex complete."
        )


if __name__ == "__main__":
    main()