"""CLI para indexar PDFs institucionais no ChromaDB."""

from indexing.pdf_loader import find_pdf_files, load_pdf_documents
from indexing.pipeline import index_documents
from shared.config import get_settings


def main() -> None:
    pdf_files = find_pdf_files()
    if not pdf_files:
        print("Nenhum PDF encontrado em data/pdfs/.")
        return

    print(f"Encontrados {len(pdf_files)} PDF(s): {[f.name for f in pdf_files]}")
    documents = load_pdf_documents(pdf_files)
    if not documents:
        print("Nenhum documento carregado.")
        return

    print(f"\nTotal de páginas carregadas: {len(documents)}")
    chunk_count = index_documents(documents)
    settings = get_settings()
    print(f"Total de chunks criados: {chunk_count}")
    print(f"Índice salvo na collection '{settings.documents_collection}'.")


if __name__ == "__main__":
    main()
