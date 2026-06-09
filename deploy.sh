#!/bin/bash
# Resume Builder 自动部署脚本
# 用法: 在服务器上执行 ./deploy.sh
set -e

echo "🚀 部署 Resume Builder..."

# 1. 拉取最新代码
git pull origin feature/test

# 2. 构建前端
echo "📦 构建前端..."
cd web && npm install --silent && npm run build && cd ..

# 3. 构建 Docker 镜像
echo "🐳 构建 Docker..."
docker build -t resume-builder:latest .

# 4. 重建容器
echo "▶️  启动服务..."
docker stop resume-builder 2>/dev/null || true
docker rm resume-builder 2>/dev/null || true
docker run -d --name resume-builder --restart unless-stopped \
  --memory=256m --memory-swap=512m \
  -p 8081:8080 \
  -e PORT=8080 \
  -e DB_TYPE=mysql \
  -e DB_HOST=172.17.0.1 \
  -e DB_PORT=3306 \
  -e DB_USER=root \
  -e DB_PASS=NFTurbo666 \
  -e DB_NAME=resume_builder \
  -e DEEPSEEK_API_KEY=sk-17095e3642e44a928d8f5bc2738c82c1 \
  resume-builder:latest

sleep 5
echo "✅ 部署完成！"
curl -s http://localhost:8081/api/health
echo ""
