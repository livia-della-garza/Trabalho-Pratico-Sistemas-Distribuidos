"""Popula a collection routing_examples no ChromaDB com exemplos FIM e RAG."""

from langchain_core.documents import Document

from shared.chroma_client import get_chroma_client, get_vectorstore
from shared.config import get_settings

ROUTING_EXAMPLES: list[tuple[str, str]] = [
    ("olá", "FIM"),
    ("oi, tudo bem?", "FIM"),
    ("bom dia", "FIM"),
    ("boa tarde", "FIM"),
    ("quem é você?", "FIM"),
    ("o que você faz?", "FIM"),
    ("obrigado pela ajuda", "FIM"),
    ("valeu", "FIM"),
    ("me fale sobre futebol", "FIM"),
    ("qual a previsão do tempo?", "FIM"),
    ("qual o prazo para entrega da dissertação?", "RAG"),
    ("quantos créditos são necessários no mestrado?", "RAG"),
    ("como funciona a qualificação do doutorado?", "RAG"),
    ("quais são os requisitos do PPGCC?", "RAG"),
    ("onde encontro o regulamento da pós-graduação?", "RAG"),
    ("qual a instrução normativa sobre bolsas?", "RAG"),
    ("como solicitar prorrogação do prazo?", "RAG"),
    ("quais formulários preciso para matrícula?", "RAG"),
    ("normas sobre publicação de artigos", "RAG"),
    ("créditos mínimos para defesa", "RAG"),
]


def main() -> None:
    settings = get_settings()
    client = get_chroma_client()

    try:
        client.delete_collection(settings.routing_collection)
        print(f"Collection '{settings.routing_collection}' removida para re-seed.")
    except Exception:
        pass

    documents = [
        Document(page_content=text, metadata={"route": route})
        for text, route in ROUTING_EXAMPLES
    ]

    vectorstore = get_vectorstore(settings.routing_collection)
    vectorstore.add_documents(documents)
    collection = settings.routing_collection
    print(f"Seed concluído: {len(documents)} exemplos em '{collection}'.")


if __name__ == "__main__":
    main()
