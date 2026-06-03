from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from indexing.paths import PDF_DATA_DIR


def find_pdf_files(extra_dirs: list[Path] | None = None) -> list[Path]:
    search_dirs = [PDF_DATA_DIR, *(extra_dirs or [])]
    pdf_files: list[Path] = []
    for directory in search_dirs:
        if directory.exists():
            pdf_files.extend(directory.glob("*.pdf"))
    return sorted(set(pdf_files))


def load_pdf_documents(pdf_files: list[Path]) -> list[Document]:
    documents: list[Document] = []
    for pdf_file in pdf_files:
        try:
            print(f"Carregando {pdf_file.name}...")
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load()
            for page in pages:
                page.metadata["source"] = pdf_file.name
            documents.extend(pages)
            print(f"  {len(pages)} página(s)")
        except Exception as exc:
            print(f"Erro ao carregar {pdf_file.name}: {exc}")
    return documents
