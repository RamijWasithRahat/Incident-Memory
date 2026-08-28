from sqlalchemy import select

from app.db.models import DocumentChunk
from app.db.session import SessionLocal
from app.services.embeddings import embed_texts


BATCH_SIZE = 32


def main() -> None:
    with SessionLocal() as db:
        chunks = list(
            db.scalars(
                select(DocumentChunk)
                .where(
                    DocumentChunk.embedding.is_(None)
                )
                .order_by(DocumentChunk.id)
            ).all()
        )

        if not chunks:
            print(
                "No chunks require embeddings."
            )
            return

        total = len(chunks)

        print(
            f"Found {total} chunks without embeddings."
        )

        updated = 0

        for start in range(
            0,
            total,
            BATCH_SIZE,
        ):
            batch = chunks[
                start:start + BATCH_SIZE
            ]

            texts = [
                chunk.chunk_text
                for chunk in batch
            ]

            vectors = embed_texts(texts)

            if len(vectors) != len(batch):
                raise RuntimeError(
                    "Embedding count does not match "
                    "chunk count."
                )

            for chunk, vector in zip(
                batch,
                vectors,
            ):
                chunk.embedding = vector

            db.commit()

            updated += len(batch)

            print(
                f"Embedded {updated}/{total} chunks."
            )

        print(
            f"Embedding complete. "
            f"Updated {updated} chunks."
        )


if __name__ == "__main__":
    main()