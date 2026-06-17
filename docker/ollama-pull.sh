#!/bin/sh
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
EMBED_MODEL="${OLLAMA_EMBED_MODEL:-qwen3-embedding:0.6b}"
CHAT_MODEL="${OLLAMA_CHAT_MODEL:-qwen3.5:0.8b}"

echo "Aguardando Ollama em ${OLLAMA_HOST}..."
until curl -sf "${OLLAMA_HOST}/api/tags" >/dev/null; do
  sleep 3
done

echo "Baixando ${EMBED_MODEL}..."
curl -sf "${OLLAMA_HOST}/api/pull" -d "{\"name\":\"${EMBED_MODEL}\",\"stream\":false}"

echo "Baixando ${CHAT_MODEL}..."
curl -sf "${OLLAMA_HOST}/api/pull" -d "{\"name\":\"${CHAT_MODEL}\",\"stream\":false}"

echo "Modelos Ollama prontos."
