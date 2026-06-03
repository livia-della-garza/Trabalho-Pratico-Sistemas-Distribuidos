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
        response = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=2.0)
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

    if settings.gemini_api_key:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        logger.info("Usando Gemini Embeddings (%s)", settings.gemini_embed_model)
        return GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embed_model,
            google_api_key=settings.gemini_api_key,
        )

    from shared.llm.hash_embeddings import HashEmbeddings

    logger.warning("Sem Ollama/Gemini; usando HashEmbeddings para desenvolvimento")
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

    if settings.gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI

        logger.info("Usando Gemini (%s)", settings.gemini_model)
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
        )

    return None


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
        result: Any = chat_model.invoke(messages)
        return str(result.content)

    if not trechos:
        return (
            "[modo sem LLM] Não encontrei trechos relevantes nos documentos indexados. "
            "Adicione PDFs em data/pdfs/ e execute o indexer."
        )

    resumo = "\n".join(
        f"- {trecho[:400]}{'...' if len(trecho) > 400 else ''}" for trecho in trechos
    )
    return (
        "[modo sem LLM] Com base nos trechos recuperados:\n\n"
        f"{resumo}\n\n"
        "Configure GEMINI_API_KEY no .env ou ative Ollama para respostas "
        "geradas por modelo de linguagem."
    )
