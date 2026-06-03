FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY src/services/rag/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/shared/ ./src/shared/
COPY src/indexing/ ./src/indexing/
COPY src/services/rag/ ./src/services/rag/

EXPOSE 8003

CMD ["uvicorn", "services.rag.main:app", "--host", "0.0.0.0", "--port", "8003"]
