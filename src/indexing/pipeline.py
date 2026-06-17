from langchain_core.documents import Document

from indexing.chunking import split_documents
from shared.chroma_client import get_chroma_client, get_vectorstore
from shared.config import get_settings
from shared.llm.embeddings import get_embeddings


def index_documents(documents: list[Document], *, reset: bool = True) -> int:
    settings = get_settings()
    splits = split_documents(documents)
    embeddings = get_embeddings()

    if reset:
        client = get_chroma_client()
        try:
            client.delete_collection(settings.documents_collection)
            collection = settings.documents_collection
            print(f"Collection '{collection}' removida para reindexação.")
        except Exception:
            pass

    vectorstore = get_vectorstore(settings.documents_collection, embeddings=embeddings)
    vectorstore.add_documents(splits)
    return len(splits)
