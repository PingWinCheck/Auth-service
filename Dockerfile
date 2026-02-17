FROM ghcr.io/astral-sh/uv:0.9.26-python3.13-bookworm-slim

RUN apt-get update && apt-get install curl -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./


RUN uv sync --no-cache --no-dev --frozen --no-install-project

COPY . .

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "--frozen", "--no-cache", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
