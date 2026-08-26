# Incident Memory

M1 starter for the RAG-Based Historical Incident Assistant.

## M1 includes

- FastAPI backend
- PostgreSQL with pgvector-ready image
- SQLAlchemy database session
- Alembic migration setup
- Docker Compose
- API + database health endpoint

## Start

```bash
cp .env.example .env
docker compose up --build
```

Open:

- API root: http://localhost:8000/
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

Expected health response:

```json
{
  "status": "ok",
  "api": "up",
  "database": "up"
}
```

## Stop

```bash
docker compose down
```
