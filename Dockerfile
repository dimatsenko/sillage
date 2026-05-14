# ─────────────────────────────────────────────
# Sillage — Django Perfume Store
# ─────────────────────────────────────────────
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Install dependencies ──────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project sources ─────────────────────
COPY . .

# ── Collect static files ─────────────────────
RUN python manage.py collectstatic --noinput || true

# ── Expose the application port ──────────────
EXPOSE 8000

# ── Default entrypoint ───────────────────────
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
