from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import os
from pathlib import Path

docs_dir = Path(__file__).parent

# Carregar todos os PDFs da pasta code
all_docs = []
pdf_files = list(docs_dir.glob("*.pdf"))

print(f"Encontrados {len(pdf_files)} arquivos PDF: {[f.name for f in pdf_files]}")

for pdf_file in pdf_files:
    try:
        print(f"Carregando {pdf_file.name}...")
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        all_docs.extend(docs)
        print(f"{len(docs)} páginas carregadas")
    except Exception as e:
        print(f"Erro ao carregar {pdf_file.name}: {e}")

print(f"\nTotal de páginas carregadas: {len(all_docs)}")

# Dividir documentos em chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

splits = text_splitter.split_documents(all_docs)
print(f"Total de chunks criados: {len(splits)}")

# Criar embeddings e armazenar no banco de dados
try:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("Índices criados e salvos em ./chroma_db")

except Exception as e:
    print(f"Erro ao criar índices: {e}")