# Python base (venv and user)
FROM python:3.10-slim AS base

RUN apt-get update && apt-get install -y build-essential curl dumb-init && rm -rf /var/lib/apt/lists/*

RUN useradd -m eddrit && \
    mkdir /app/ && \
    chown -R eddrit /app/
USER eddrit

# Install Poetry and dumb-init
ENV PATH="${PATH}:/home/eddrit/.poetry/bin"
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    poetry config virtualenvs.in-project true

# Dependencies
WORKDIR /app/
COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry install --no-interaction --no-ansi --no-root --no-dev


# Prod image (app and default config)
FROM python:3.10-slim as prod

COPY --from=base /usr/bin/dumb-init /usr/bin/
COPY --from=base /app /app

WORKDIR /app/

# App
COPY eddrit /app/eddrit
COPY static /app/static
COPY templates /app/templates

# Default log level
ENV LOG_LEVEL=WARNING

# Expose and run app
EXPOSE 8080
CMD ["dumb-init", "/app/.venv/bin/gunicorn", "eddrit.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "--log-file=-"]
