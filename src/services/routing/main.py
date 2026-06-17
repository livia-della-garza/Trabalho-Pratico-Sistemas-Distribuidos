import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from shared.chroma_client import get_vectorstore
from shared.config import get_settings
from shared.db.routing import RoutingLog, get_session, init_db
from shared.models import ClassificarResponse, PerguntaRequest, Rota

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Routing Service", lifespan=lifespan)


def _score_to_similarity(score: float) -> float:
    return max(0.0, min(1.0, 1.0 - score))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/classificar", response_model=ClassificarResponse)
def classificar(
    body: PerguntaRequest,
    session: Session = Depends(get_session),
) -> ClassificarResponse:
    settings = get_settings()
    vectorstore = get_vectorstore(settings.routing_collection)

    pergunta = body.pergunta.strip()
    results = vectorstore.similarity_search_with_score(pergunta, k=1)

    if not results:
        decisao = Rota.FIM
        score = 0.0
    else:
        doc, distance = results[0]
        route_meta = doc.metadata.get("route", "FIM")
        decisao = Rota.RAG if route_meta == "RAG" else Rota.FIM
        score = _score_to_similarity(float(distance))

    session.add(
        RoutingLog(
            pergunta=pergunta,
            decisao=decisao.value,
            score=score,
        )
    )

    logger.info("Rota classificada: %s (score=%.3f)", decisao.value, score)
    return ClassificarResponse(decisao=decisao, score=score)
