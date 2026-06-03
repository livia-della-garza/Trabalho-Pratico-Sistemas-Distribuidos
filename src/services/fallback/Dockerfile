FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY src/services/fallback/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/shared/ ./src/shared/
COPY src/services/fallback/ ./src/services/fallback/

EXPOSE 8002

CMD ["uvicorn", "services.fallback.main:app", "--host", "0.0.0.0", "--port", "8002"]
