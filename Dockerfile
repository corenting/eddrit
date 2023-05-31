# Python base (venv and user)
FROM python:3.11-slim AS base

# Install dependencies and dumb-init
RUN apt-get update && apt-get install -y build-essential curl dumb-init && rm -rf /var/lib/apt/lists/*

RUN useradd -m eddrit && \
    mkdir /app/ && \
    chown -R eddrit /app/
USER eddrit

# Install Poetry
ENV PATH="${PATH}:/home/eddrit/.local/bin"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.in-project true

# Dependencies
WORKDIR /app/
COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry install --no-interaction --no-root --only main


# Prod image (app and default config)
FROM python:3.11-slim as prod

COPY --from=base /usr/bin/dumb-init /usr/bin/
COPY --from=base /app /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/

# User
RUN useradd -m eddrit && \
    chown -R eddrit /app/
USER eddrit

# App
COPY eddrit /app/eddrit
COPY static /app/static
COPY templates /app/templates

# Default log level
ENV LOG_LEVEL=WARNING

# Expose and run app
EXPOSE 8080
CMD ["dumb-init", "/app/.venv/bin/gunicorn", "eddrit.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "--log-file=-"]
