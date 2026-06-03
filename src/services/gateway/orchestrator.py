import logging

import httpx

from shared.config import get_settings
from shared.models import Rota

logger = logging.getLogger(__name__)


async def processar_pergunta(pergunta: str) -> dict[str, str]:
    settings = get_settings()
    pergunta = pergunta.strip()
    if not pergunta:
        raise ValueError("Pergunta não pode ser vazia")

    async with httpx.AsyncClient(timeout=120.0) as client:
        routing_resp = await client.post(
            f"{settings.routing_url}/classificar",
            json={"pergunta": pergunta},
        )
        routing_resp.raise_for_status()
        routing_data = routing_resp.json()
        decisao = routing_data["decisao"]

        if decisao == Rota.FIM.value:
            service_resp = await client.post(
                f"{settings.fallback_url}/responder",
                json={"pergunta": pergunta},
            )
        else:
            service_resp = await client.post(
                f"{settings.rag_url}/processar",
                json={"pergunta": pergunta},
            )

        service_resp.raise_for_status()
        service_data = service_resp.json()

    resposta = service_data["resposta"]
    logger.info("Pergunta processada via rota %s", decisao)
    return {"resposta": resposta, "rota": decisao}
