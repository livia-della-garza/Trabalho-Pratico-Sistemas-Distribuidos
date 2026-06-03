from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from shared.chroma_client import get_vectorstore
from shared.config import get_settings
from shared.llm.embeddings import get_embeddings


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_documents(documents)


def index_documents(documents: list[Document]) -> int:
    settings = get_settings()
    splits = split_documents(documents)
    embeddings = get_embeddings()
    vectorstore = get_vectorstore(settings.documents_collection, embeddings=embeddings)
    vectorstore.add_documents(splits)
    return len(splits)
