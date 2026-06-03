import hashlib

from langchain_core.embeddings import Embeddings


class HashEmbeddings(Embeddings):
    """Embeddings determinísticos derivados do texto (para dev sem Ollama)."""

    def __init__(self, size: int = 384) -> None:
        self.size = size

    def _embed(self, text: str) -> list[float]:
        vec: list[float] = []
        seed = text.lower().strip()
        for i in range(self.size):
            digest = hashlib.sha256(f"{seed}:{i}".encode()).digest()
            value = int.from_bytes(digest[:4], "big") / 2**32
            vec.append(value * 2.0 - 1.0)
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
