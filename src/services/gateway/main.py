import json
import logging

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from services.gateway.orchestrator import processar_pergunta

logger = logging.getLogger(__name__)

mcp = FastMCP("AcademicAssistant")


@mcp.tool()
async def enviar_pergunta(pergunta: str) -> str:
    """Recebe uma pergunta do usuário, roteia para FIM ou RAG e devolve a resposta."""
    resultado = await processar_pergunta(pergunta)
    return resultado["resposta"]


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "gateway"})


async def websocket_handler(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "erro", "message": "Mensagem inválida: JSON esperado"}
                )
                continue

            msg_type = payload.get("type")
            if msg_type != "pergunta":
                await websocket.send_json(
                    {"type": "erro", "message": f"Tipo desconhecido: {msg_type}"}
                )
                continue

            texto = str(payload.get("text", "")).strip()
            if not texto:
                await websocket.send_json(
                    {"type": "erro", "message": "Campo 'text' não pode ser vazio"}
                )
                continue

            try:
                resultado = await processar_pergunta(texto)
                await websocket.send_json(
                    {
                        "type": "resposta",
                        "text": resultado["resposta"],
                        "rota": resultado["rota"],
                    }
                )
            except Exception as exc:
                logger.exception("Erro ao processar pergunta via WebSocket")
                await websocket.send_json(
                    {"type": "erro", "message": f"Erro interno: {exc}"}
                )
    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado")


mcp_app = mcp.http_app()

app = Starlette(
    routes=[
        WebSocketRoute("/ws", websocket_handler),
        Mount("/", app=mcp_app),
    ],
    lifespan=mcp_app.lifespan,
)
