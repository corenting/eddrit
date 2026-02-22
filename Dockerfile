# Python base (venv and user)
FROM python:3.14 AS base

# Install dumb-init
RUN apt-get update && apt-get install -y dumb-init

# Create user
RUN useradd -m eddrit && \
    mkdir /app/ && \
    chown -R eddrit /app/
USER eddrit

# Install dependencies that don't have wheels
# for some architectures directly so that they can be cached.
# To keep in sync with poetry.lock to speedup CI
RUN /usr/local/bin/pip install --user \
    uvloop==0.22.1 \
    httptools==0.7.1 \
    MarkupSafe==3.0.3 \
    pyyaml==6.0.3

# Create a fake eddrit package to install dependencies
WORKDIR /app/
RUN mkdir /app/eddrit
COPY eddrit/__init__.py /app/eddrit/

# Install dependencies with poetry with only the needed files
COPY pyproject.toml poetry.lock README.md /app/
ENV CPPFLAGS=-I/usr/local/include/python3.14/ \
    PATH=/home/eddrit/.local/bin:$PATH
RUN /usr/local/bin/pip install --user .

# Prod image (app and default config)
FROM python:3.14-slim AS prod

COPY --from=base /home/eddrit/.local /home/eddrit/.local
COPY --from=base /usr/bin/dumb-init /usr/bin/

WORKDIR /app/

# User
RUN useradd -m eddrit && \
    chown -R eddrit /app/ && \
    chown -R eddrit /home/eddrit/
USER eddrit

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/eddrit/.local/bin:$PATH

# App
COPY eddrit /app/eddrit
COPY static /app/static
COPY templates /app/templates

# Default log level
ENV LOG_LEVEL=WARNING
ENV FORWARDED_ALLOWED_IP="127.0.0.1,::1"

# Expose and run app
EXPOSE 8080
ENTRYPOINT ["dumb-init", "--"]
CMD ["gunicorn", "eddrit.app:app", "--workers", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
