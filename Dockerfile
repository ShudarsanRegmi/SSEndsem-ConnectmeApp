# Multi-Stage Hardened Dockerfile for ConnectMe
# Stage 1: Build Dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Hardened Runtime Container
FROM python:3.12-slim AS runner

WORKDIR /app

# Install minimal runtime utilities (curl for health check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dedicated Non-Root User (UID 10001)
RUN groupadd -g 10001 connectme && \
    useradd -u 10001 -g connectme -m -s /bin/bash appuser

# Copy installed python site-packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Ensure path includes user site-packages
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code and built React frontend
COPY --chown=appuser:connectme app/ /app/app/
COPY --chown=appuser:connectme frontend/dist/ /app/frontend/dist/

# Create and configure isolated non-executable media upload directory
RUN mkdir -p /app/secure_media && \
    chown -R appuser:connectme /app/secure_media && \
    chmod 750 /app/secure_media

# Switch execution context to non-root user
USER appuser

EXPOSE 8000

# Health check instruction
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
