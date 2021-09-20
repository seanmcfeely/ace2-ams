FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/app/ /app