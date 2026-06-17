"""CLI para indexar normas (Markdown e PDF) no ChromaDB."""

from indexing.md_loader import find_md_files, load_md_documents
from indexing.pdf_loader import find_pdf_files, load_pdf_documents
from indexing.pipeline import index_documents
from shared.config import get_settings


def main() -> None:
    md_files = find_md_files()
    pdf_files = find_pdf_files()

    if not md_files and not pdf_files:
        print("Nenhum arquivo encontrado em data/md/ ou data/pdfs/.")
        return

    documents = []
    if md_files:
        print(f"Encontrados {len(md_files)} Markdown(s).")
        documents.extend(load_md_documents(md_files))
    if pdf_files:
        print(f"Encontrados {len(pdf_files)} PDF(s): {[f.name for f in pdf_files]}")
        documents.extend(load_pdf_documents(pdf_files))

    if not documents:
        print("Nenhum documento carregado.")
        return

    print(f"\nTotal de documentos carregados: {len(documents)}")
    chunk_count = index_documents(documents)
    settings = get_settings()
    print(f"Total de chunks criados: {chunk_count}")
    print(f"Índice salvo na collection '{settings.documents_collection}'.")


if __name__ == "__main__":
    main()
