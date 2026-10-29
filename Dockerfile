# 单容器部署：前端构建产物内置到 Django，由 WhiteNoise + SPA 兜底直接托管。
# 适合只允许暴露一个端口的托管平台（Render / Railway / 自建 Docker 等）。
FROM node:22-alpine AS web

WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=False \
    DJANGO_SQLITE_PATH=/app/data/db.sqlite3

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=web /web/dist ./frontend_dist

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["sh", "entrypoint.sh"]
