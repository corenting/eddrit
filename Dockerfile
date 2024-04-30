# Python base (venv and user)
FROM python:3.12 AS base

# Install dumb-init
RUN apt-get update && apt-get install -y dumb-init

RUN useradd -m eddrit && \
    mkdir /app/ && \
    chown -R eddrit /app/
USER eddrit

# Dependencies
WORKDIR /app/
COPY . /app/
ENV CPPFLAGS=-I/usr/local/include/python3.12/ \
    PATH=/home/eddrit/.local/bin:$PATH
RUN /usr/local/bin/pip install --user .

# Prod image (app and default config)
FROM python:3.12-slim as prod

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
CMD ["gunicorn", "eddrit.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "--log-file=-"]
