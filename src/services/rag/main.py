import json
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from shared.chroma_client import get_vectorstore
from shared.config import get_settings
from shared.db.rag import RagInteraction, get_session, init_db
from shared.llm.embeddings import generate_rag_response
from shared.models import FonteDocumento, PerguntaRequest, ProcessarResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="RAG Service", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/processar", response_model=ProcessarResponse)
def processar(
    body: PerguntaRequest,
    session: Session = Depends(get_session),
) -> ProcessarResponse:
    settings = get_settings()
    vectorstore = get_vectorstore(settings.documents_collection)

    pergunta = body.pergunta.strip()
    docs = vectorstore.similarity_search(pergunta, k=settings.rag_top_k)

    fontes = [
        FonteDocumento(conteudo=doc.page_content, metadata=dict(doc.metadata))
        for doc in docs
    ]
    trechos = [fonte.conteudo for fonte in fontes]
    resposta = generate_rag_response(pergunta, trechos)

    session.add(
        RagInteraction(
            pergunta=pergunta,
            resposta=resposta,
            chunks_json=json.dumps(
                [
                    {"conteudo": f.conteudo[:500], "metadata": f.metadata}
                    for f in fontes
                ],
                ensure_ascii=False,
            ),
        )
    )

    logger.info("Resposta RAG gerada (%d trechos)", len(fontes))
    return ProcessarResponse(resposta=resposta, fontes=fontes)
