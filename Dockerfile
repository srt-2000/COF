ARG INSTALL_DEV_DEPS=false

FROM python:3.12-slim

ARG INSTALL_DEV_DEPS
RUN echo "INSTALL_DEV_DEPS value: $INSTALL_DEV_DEPS"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        echo "Installing with TEST dependencies..." && \
        uv sync --frozen --group dev; \
    else \
        echo "Installing only main dependencies..." && \
        uv sync --frozen --no-dev; \
    fi

COPY ./coffeeshop/ ./coffeeshop/