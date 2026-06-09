.PHONY: dev build run clean

# 安装依赖
install:
	cd web && npm install
	pip install -r requirements.txt

# 开发模式
dev:
	cd web && npm run dev &
	uvicorn server.main:app --reload --port 8080

# 构建前端
build-web:
	cd web && npm install && npm run build

# 完整构建
build: build-web
	docker build -t resume-builder:latest .

# 本地运行
run:
	uvicorn server.main:app --host 0.0.0.0 --port 8080

# Docker 运行
docker-run:
	docker run -d --name resume-builder --restart unless-stopped \
	  -e DB_HOST=host.docker.internal -e DB_PORT=3306 \
	  -e DB_USER=root -e DB_PASS=${DB_PASS} -e DB_NAME=resume_builder \
	  -e DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY} \
	  -p 8081:8080 resume-builder:latest

# 清理
clean:
	rm -rf web/node_modules web/dist server/__pycache__ server/**/__pycache__
