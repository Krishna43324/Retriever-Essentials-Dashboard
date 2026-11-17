FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached until requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend

# Run as a non-root user; uploads/ is the volume-mounted upload directory.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/uploads \
    && chown -R appuser:appuser /app
USER appuser

ENV UPLOAD_DIR=/app/uploads \
    PORT=5000

EXPOSE 5000

# --preload runs the DB wait + admin bootstrap once, before workers fork.
CMD ["sh", "-c", "exec gunicorn --chdir backend --preload --workers 2 --bind 0.0.0.0:${PORT} flask_start:app"]
