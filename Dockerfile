# 阶段 1：构建前端
FROM node:20-alpine AS web-builder
WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm install
COPY web/ ./
RUN npm run build

# 阶段 2：构建后端
FROM golang:1.21-alpine AS server-builder
WORKDIR /app
COPY server/ ./
COPY --from=web-builder /web/dist ./static
RUN go mod download && CGO_ENABLED=0 go build -o resume-builder .

# 阶段 3：运行
FROM alpine:3.19
WORKDIR /app
COPY --from=server-builder /app/resume-builder .
EXPOSE 8080
ENTRYPOINT ["./resume-builder"]
