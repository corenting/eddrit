# Python base (venv and user)
FROM python:3.13 AS base

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
    uvloop==0.21.0 \
    lxml==5.3.2 \
    httptools==0.6.4 \
    MarkupSafe==3.0.2 \
    pyyaml==6.0.2

# Dependencies
WORKDIR /app/
COPY . /app/
ENV CPPFLAGS=-I/usr/local/include/python3.13/ \
    PATH=/home/eddrit/.local/bin:$PATH
RUN /usr/local/bin/pip install --user .

# Prod image (app and default config)
FROM python:3.13-slim AS prod

COPY --from=base /home/eddrit/.local /home/eddrit/.local
COPY --from=base /usr/bin/dumb-init /usr/bin/
COPY --from=base /app /app

# User
RUN useradd -m eddrit && \
    chown -R eddrit /app/ && \
    chown -R eddrit /home/eddrit/
USER eddrit

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/eddrit/.local/bin:$PATH
WORKDIR /app/

# App
COPY eddrit /app/eddrit
COPY static /app/static
COPY templates /app/templates

# Default log level
ENV LOG_LEVEL=WARNING

# Expose and run app
EXPOSE 8080
ENTRYPOINT ["dumb-init", "--"]
CMD ["uvicorn", "eddrit.app:app", "--workers", "2", "--host", "0.0.0.0", "--port", "8080"]
