import os
from functools import lru_cache


@lru_cache
def get_settings() -> "Settings":
    return Settings()


class Settings:
    def __init__(self) -> None:
        self.ollama_enabled = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.ollama_embed_model = os.getenv(
            "OLLAMA_EMBED_MODEL", "qwen3-embedding:0.6b"
        )

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8004"))

        self.routing_postgres_dsn = os.getenv(
            "ROUTING_POSTGRES_DSN",
            "postgresql://academic:academic@localhost:5433/routing",
        )
        self.fallback_postgres_dsn = os.getenv(
            "FALLBACK_POSTGRES_DSN",
            "postgresql://academic:academic@localhost:5434/fallback",
        )
        self.rag_postgres_dsn = os.getenv(
            "RAG_POSTGRES_DSN",
            "postgresql://academic:academic@localhost:5435/rag",
        )

        self.routing_url = os.getenv("ROUTING_URL", "http://localhost:8001")
        self.fallback_url = os.getenv("FALLBACK_URL", "http://localhost:8002")
        self.rag_url = os.getenv("RAG_URL", "http://localhost:8003")
        self.gateway_ws_url = os.getenv("GATEWAY_WS_URL", "ws://localhost:8000/ws")

        self.routing_collection = os.getenv("ROUTING_COLLECTION", "routing_examples")
        self.documents_collection = os.getenv("DOCUMENTS_COLLECTION", "documents")
        self.rag_top_k = int(os.getenv("RAG_TOP_K", "4"))
