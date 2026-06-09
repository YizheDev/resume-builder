# 阶段 1：构建前端
FROM node:20-alpine AS web-builder
WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm install
COPY web/ ./
RUN npm run build

# 阶段 2：Python 运行环境
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（WeasyPrint 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev libcairo2 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/
COPY --from=web-builder /web/dist ./static/

EXPOSE 8080
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
