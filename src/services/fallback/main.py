import logging
import re
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from shared.db.postgres import FimInteraction, get_session, init_db
from shared.models import PerguntaRequest, ResponderResponse

logger = logging.getLogger(__name__)

TEMPLATES: dict[str, dict[str, str]] = {
    "saudacao": {
        "patterns": r"\b(ol[aá]|oi|bom dia|boa tarde|boa noite|e a[ií]|hey|hello)\b",
        "resposta": (
            "Olá! Sou o Assistente Acadêmico Inteligente da pós-graduação do DCC/UFLA. "
            "Posso ajudar com regulamentos, instruções normativas, resoluções, "
            "formulários e rotinas acadêmicas. Como posso ajudar?"
        ),
    },
    "escopo": {
        "patterns": (
            r"\b(quem [eé] voc[eê]|o que voc[eê] faz|"
            r"para que serve|ajuda com o qu[eê])\b"
        ),
        "resposta": (
            "Sou especializado em informações acadêmicas da pós-graduação do DCC/UFLA, "
            "com base em documentos institucionais oficiais. "
            "Pergunte sobre prazos, requisitos, normas ou procedimentos acadêmicos."
        ),
    },
    "despedida": {
        "patterns": r"\b(obrigad[oa]|valeu|tchau|at[eé] logo|at[eé] mais|bye)\b",
        "resposta": (
            "Por nada! Se precisar de mais informações sobre a pós-graduação, "
            "estou à disposição. Bons estudos!"
        ),
    },
    "fora_escopo": {
        "patterns": r"\b(futebol|clima|tempo|receita|piada|pol[ií]tica)\b",
        "resposta": (
            "Desculpe, essa pergunta está fora do meu escopo. "
            "Atendo apenas dúvidas sobre normas e rotinas acadêmicas "
            "da pós-graduação do DCC/UFLA."
        ),
    },
    "default": {
        "patterns": "",
        "resposta": (
            "Não identifiquei uma pergunta específica sobre normas acadêmicas. "
            "Por favor, reformule sua dúvida sobre regulamentos, prazos, "
            "requisitos ou procedimentos da pós-graduação."
        ),
    },
}


def selecionar_resposta_padrao(pergunta: str) -> tuple[str, str]:
    texto = pergunta.lower().strip()
    for template_id, template in TEMPLATES.items():
        if template_id == "default":
            continue
        if re.search(template["patterns"], texto, re.IGNORECASE):
            return template["resposta"], template_id
    return TEMPLATES["default"]["resposta"], "default"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Fallback Service", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/responder", response_model=ResponderResponse)
def responder(
    body: PerguntaRequest,
    session: Session = Depends(get_session),
) -> ResponderResponse:
    pergunta = body.pergunta.strip()
    resposta, template_id = selecionar_resposta_padrao(pergunta)

    session.add(
        FimInteraction(
            pergunta=pergunta,
            resposta=resposta,
            template_id=template_id,
        )
    )

    logger.info("Resposta FIM gerada (template=%s)", template_id)
    return ResponderResponse(resposta=resposta, template_id=template_id)
