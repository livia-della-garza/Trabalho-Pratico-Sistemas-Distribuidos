from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Rota(StrEnum):
    FIM = "FIM"
    RAG = "RAG"


class PerguntaRequest(BaseModel):
    pergunta: str = Field(min_length=1)


class ClassificarResponse(BaseModel):
    decisao: Rota
    score: float


class ResponderResponse(BaseModel):
    resposta: str
    template_id: str


class FonteDocumento(BaseModel):
    conteudo: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProcessarResponse(BaseModel):
    resposta: str
    fontes: list[FonteDocumento] = Field(default_factory=list)


class RespostaGateway(BaseModel):
    resposta: str
    rota: Rota
