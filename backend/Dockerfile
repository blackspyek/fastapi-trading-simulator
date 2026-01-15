FROM python:3.12-slim AS test

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PROJECT_NAME="Test App"
ENV DATABASE_URL="postgresql+asyncpg://test_user:test_pass@localhost/test_db"
ENV SECRET_KEY="test_secret_key_for_build_process"
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30

RUN python -m pytest -v --tb=short
RUN touch /tmp/test_completed_successfully

FROM python:3.12-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=test /tmp/test_completed_successfully /tmp/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY seed.py .
COPY run.sh .
RUN chmod +x run.sh && sed -i 's/\r$//' run.sh

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["./run.sh"]
