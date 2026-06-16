# ── Stage 1: Build dependencies ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install TA-Lib (requires compiled C library)
RUN curl -fsSL https://github.com/TA-Lib/ta-lib/releases/download/v0.6.0/ta-lib-0.6.0-src.tar.gz \
    -o ta-lib.tar.gz \
    && tar -xzf ta-lib.tar.gz \
    && cd ta-lib-0.6.0 \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && ldconfig

# Copy dependency files and install into a venv
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled TA-Lib libraries from builder
COPY --from=builder /usr/lib/libta_lib* /usr/lib/
COPY --from=builder /usr/include/ta-lib /usr/include/ta-lib
RUN ldconfig

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r cryptoapp && useradd -r -g cryptoapp -d /app cryptoapp

WORKDIR /app
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

RUN chown -R cryptoapp:cryptoapp /app
USER cryptoapp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
