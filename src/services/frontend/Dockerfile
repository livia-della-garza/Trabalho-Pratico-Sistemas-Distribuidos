FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY src/services/frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/services/frontend/ ./src/services/frontend/

EXPOSE 8501

CMD ["streamlit", "run", "src/services/frontend/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
