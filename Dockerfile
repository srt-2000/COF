ARG INSTALL_DEV_DEPS=false

FROM python:3.12-slim

ARG INSTALL_DEV_DEPS
RUN echo "INSTALL_DEV_DEPS value: $INSTALL_DEV_DEPS"
RUN pip install --upgrade pip
RUN pip install poetry==2.1.4

ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1\
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache\
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock .
COPY ./coffeeshop/ ./coffeeshop/
RUN touch README.md

RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        echo "Installing with TEST dependencies..." && \
        poetry install --no-root --no-cache ; \
    else \
        echo "Installing only main dependencies..." && \
        poetry install --without dev --no-root --no-cache ; \
    fi