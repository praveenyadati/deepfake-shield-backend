FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

# Install Python deps first for better build cache
COPY requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r /srv/requirements.txt

# App code
COPY app /srv/app

# SQLite lives on a mounted volume so data survives container restarts
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8000

# Run as a non-root user
RUN useradd --create-home --uid 10001 shield && chown -R shield:shield /srv /data
USER shield

# Honors $PORT when set (Railway / Fly / Render); falls back to 8000 for local Docker.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
