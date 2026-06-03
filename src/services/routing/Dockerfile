FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY src/services/routing/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/shared/ ./src/shared/
COPY src/scripts/ ./src/scripts/
COPY src/services/routing/ ./src/services/routing/

EXPOSE 8001

CMD ["uvicorn", "services.routing.main:app", "--host", "0.0.0.0", "--port", "8001"]
