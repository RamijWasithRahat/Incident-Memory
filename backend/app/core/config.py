from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "Incident Memory API"
    app_env: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://"
        "incident_memory:"
        "incident_memory@db:5432/"
        "incident_memory"
    )

    # M4 - Embedding model
    embedding_model: str = (
        "BAAI/bge-small-en-v1.5"
    )
    embedding_dimension: int = 384

    # M6 - Free local Hugging Face LLM
    llm_model: str = (
        "Qwen/Qwen2.5-0.5B-Instruct"
    )
    llm_max_new_tokens: int = 400

    # M6 - RAG configuration
    rag_top_k: int = 5
    rag_min_similarity: float = 0.45
    rag_max_context_chars: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()