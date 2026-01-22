FROM ghcr.io/astral-sh/uv:0.9.26-python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./


RUN uv sync --no-cache --no-dev --frozen --no-install-project

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
