import logging
from typing import Any

import httpx
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from shared.config import get_settings

logger = logging.getLogger(__name__)


def _ollama_reachable(base_url: str) -> bool:
    try:
        response = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=5.0)
        return response.status_code == 200
    except (httpx.HTTPError, OSError):
        return False


def get_embeddings() -> Embeddings:
    settings = get_settings()
    if settings.ollama_enabled and _ollama_reachable(settings.ollama_base_url):
        from langchain_ollama import OllamaEmbeddings

        logger.info("Usando OllamaEmbeddings (%s)", settings.ollama_embed_model)
        return OllamaEmbeddings(
            model=settings.ollama_embed_model,
            base_url=settings.ollama_base_url,
        )

    from shared.llm.hash_embeddings import HashEmbeddings

    logger.warning(
        "Ollama indisponível; usando HashEmbeddings (apenas desenvolvimento)"
    )
    return HashEmbeddings(size=384)


def get_chat_model() -> BaseChatModel | None:
    settings = get_settings()
    if settings.ollama_enabled and _ollama_reachable(settings.ollama_base_url):
        from langchain_ollama import ChatOllama

        logger.info("Usando ChatOllama (%s)", settings.ollama_chat_model)
        return ChatOllama(
            model=settings.ollama_chat_model,
            base_url=settings.ollama_base_url,
        )

    return None


def _stub_rag_response(trechos: list[str], aviso_llm: str | None = None) -> str:
    if not trechos:
        return (
            "[modo sem LLM] Não encontrei trechos relevantes nos documentos indexados. "
            "Adicione arquivos em data/md/ ou data/pdfs/ e execute o indexer."
        )

    resumo = "\n".join(
        f"- {trecho[:400]}{'...' if len(trecho) > 400 else ''}" for trecho in trechos
    )
    aviso = aviso_llm or (
        "Inicie o Ollama e baixe qwen3-embedding:0.6b e qwen3.5:0.8b "
        "para respostas geradas por modelo de linguagem."
    )
    return f"[modo sem LLM] Com base nos trechos recuperados:\n\n{resumo}\n\n{aviso}"


def generate_rag_response(pergunta: str, trechos: list[str]) -> str:
    contexto = "\n\n---\n\n".join(trechos) if trechos else "Nenhum trecho encontrado."

    chat_model = get_chat_model()
    if chat_model is not None:
        messages = [
            SystemMessage(
                content=(
                    "Você é um assistente acadêmico da pós-graduação do DCC/UFLA. "
                    "Responda com base apenas nos trechos fornecidos. "
                    "Se a informação não estiver nos trechos, "
                    "diga que não encontrou nos documentos."
                )
            ),
            HumanMessage(
                content=(
                    f"Pergunta: {pergunta}\n\n"
                    f"Trechos relevantes:\n{contexto}\n\n"
                    "Responda de forma clara e objetiva em português."
                )
            ),
        ]
        try:
            result: Any = chat_model.invoke(messages)
            return str(result.content)
        except Exception as exc:
            logger.warning("LLM indisponível (%s); usando fallback com trechos", exc)
            return _stub_rag_response(
                trechos,
                aviso_llm=(
                    "O modelo Ollama está indisponível no momento. "
                    "Verifique se qwen3.5:0.8b e qwen3-embedding:0.6b foram baixados."
                ),
            )

    return _stub_rag_response(trechos)
