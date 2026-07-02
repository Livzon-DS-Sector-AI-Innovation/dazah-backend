FROM python:3.12-slim

WORKDIR /app

# 安装 PostgreSQL 客户端（pg_isready / psql），用于 entrypoint.sh 检测数据库和导入 dump
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

# 确保 .env 和 dump.sql 存在（演示用途，秘钥和数据打包进镜像）
COPY .env /app/.env
COPY dump.sql /app/dump.sql

# 设置启动脚本权限
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
