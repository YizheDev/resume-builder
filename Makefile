.PHONY: dev build run clean

# 开发模式
dev:
	cd web && npm run dev

# 构建前端
build-web:
	cd web && npm install && npm run build

# 构建后端
build-server:
	cd server && go build -o resume-builder .

# 完整构建
build: build-web build-server

# 本地运行
run:
	cd server && go run .

# 清理
clean:
	rm -rf server/resume-builder server/static web/node_modules
