import chromadb
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from shared.config import get_settings
from shared.llm.embeddings import get_embeddings


def get_chroma_client() -> chromadb.HttpClient:
    settings = get_settings()
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def get_vectorstore(
    collection_name: str,
    embeddings: Embeddings | None = None,
) -> Chroma:
    client = get_chroma_client()
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings or get_embeddings(),
    )
