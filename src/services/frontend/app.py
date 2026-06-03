import asyncio
import json
import logging
import os
import queue
import threading
from typing import Any

import streamlit as st
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GATEWAY_WS_URL = os.getenv("GATEWAY_WS_URL", "ws://localhost:8000/ws")


class WebSocketClient:
    def __init__(self, url: str) -> None:
        self.url = url
        self.incoming: queue.Queue[dict[str, Any]] = queue.Queue()
        self._send_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._thread: threading.Thread | None = None
        self._started = False
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def send_pergunta(self, text: str) -> None:
        payload = json.dumps({"type": "pergunta", "text": text}, ensure_ascii=False)
        asyncio.run_coroutine_threadsafe(self._send_queue.put(payload), self._loop)

    def poll_messages(self) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        while True:
            try:
                messages.append(self.incoming.get_nowait())
            except queue.Empty:
                break
        return messages

    def _run_loop(self) -> None:
        asyncio.run(self._connect_and_listen())

    async def _connect_and_listen(self) -> None:
        self._loop = asyncio.get_running_loop()
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    logger.info("Conectado ao gateway: %s", self.url)
                    await asyncio.gather(
                        self._receiver(ws),
                        self._sender(ws),
                    )
            except Exception as exc:
                logger.warning("Conexão WebSocket perdida (%s); reconectando...", exc)
                await asyncio.sleep(2)

    async def _receiver(self, ws: websockets.WebSocketClientProtocol) -> None:
        async for raw in ws:
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                message = {"type": "erro", "message": "Resposta inválida do gateway"}
            self.incoming.put(message)

    async def _sender(self, ws: websockets.WebSocketClientProtocol) -> None:
        while True:
            payload = await self._send_queue.get()
            if payload is None:
                return
            await ws.send(payload)


def init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ws_client" not in st.session_state:
        client = WebSocketClient(GATEWAY_WS_URL)
        client.start()
        st.session_state.ws_client = client
    if "pending" not in st.session_state:
        st.session_state.pending = False


def main() -> None:
    st.set_page_config(
        page_title="Assistente Acadêmico Inteligente",
        page_icon="🎓",
        layout="centered",
    )
    init_session()

    st.title("Assistente Acadêmico Inteligente")
    st.caption("Pós-graduação DCC/UFLA — comunicação via WebSocket com o Gateway MCP")

    client: WebSocketClient = st.session_state.ws_client
    for msg in client.poll_messages():
        msg_type = msg.get("type")
        if msg_type == "resposta":
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": msg.get("text", ""),
                    "rota": msg.get("rota"),
                }
            )
            st.session_state.pending = False
        elif msg_type == "erro":
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Erro: {msg.get('message', 'desconhecido')}",
                }
            )
            st.session_state.pending = False

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("rota"):
                st.caption(f"Rota: {message['rota']}")

    if st.session_state.pending:
        with st.chat_message("assistant"):
            st.markdown("_Processando..._")

    prompt = st.chat_input("Digite sua pergunta sobre normas acadêmicas...")
    if prompt and not st.session_state.pending:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending = True
        client.send_pergunta(prompt)
        st.rerun()

    if st.session_state.pending:
        import time

        time.sleep(0.3)
        st.rerun()


if __name__ == "__main__":
    main()
