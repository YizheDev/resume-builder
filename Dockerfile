FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn python-multipart sqlalchemy pymysql pydantic httpx python-dotenv Pillow

COPY server/ ./server/
COPY server/static/ ./static/

ENV PORT=8080
EXPOSE 8080
CMD uvicorn server.main:app --host 0.0.0.0 --port $PORT
