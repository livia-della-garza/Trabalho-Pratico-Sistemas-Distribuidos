from pathlib import Path

from langchain_core.documents import Document

from indexing.paths import MD_DATA_DIR


def find_md_files(extra_dirs: list[Path] | None = None) -> list[Path]:
    search_dirs = [MD_DATA_DIR, *(extra_dirs or [])]
    md_files: list[Path] = []
    for directory in search_dirs:
        if directory.exists():
            md_files.extend(directory.glob("*.md"))
    return sorted(set(md_files))


def load_md_documents(md_files: list[Path]) -> list[Document]:
    documents: list[Document] = []
    for md_file in md_files:
        try:
            print(f"Carregando {md_file.name}...")
            text = md_file.read_text(encoding="utf-8")
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": md_file.name, "format": "md"},
                )
            )
        except Exception as exc:
            print(f"Erro ao carregar {md_file.name}: {exc}")
    return documents
