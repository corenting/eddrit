# Builder (install dependencies into a venv)
FROM ghcr.io/corenting/base-container-images/python-3.14:latest AS builder

# Create venv
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create a fake eddrit package to install dependencies
RUN mkdir /app/eddrit
COPY eddrit/__init__.py /app/eddrit/

# Install dependencies
COPY pyproject.toml poetry.lock README.md /app/
RUN pip install --no-cache-dir /app/

# Prod image
FROM ghcr.io/corenting/base-container-images/python-3.14:latest AS prod

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# App
COPY --chown=nonroot:nonroot eddrit /app/eddrit
COPY --chown=nonroot:nonroot static /app/static
COPY --chown=nonroot:nonroot templates /app/templates

# Default log level
ENV LOG_LEVEL=WARNING
ENV FORWARDED_ALLOWED_IP="127.0.0.1,::1"

# Expose and run app
EXPOSE 8080
CMD ["gunicorn", "eddrit.app:app", "--workers", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
