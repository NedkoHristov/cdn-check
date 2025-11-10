# Multi-stage build for minimal image size
# Stage 1: Builder
FROM python:3.11-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-alpine

# Build arguments for version info
ARG APP_VERSION=dev
ARG BUILD_TIME=unknown

# Set working directory
WORKDIR /app

# Create non-root user for security (before copying files)
RUN adduser -D -u 1000 appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    WORKERS=4 \
    APP_VERSION=${APP_VERSION} \
    BUILD_TIME=${BUILD_TIME}

# Copy Python dependencies from builder to appuser home
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser templates/ templates/
COPY --chown=appuser:appuser static/ static/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/', timeout=5)" || exit 1

# Run gunicorn
CMD gunicorn -w ${WORKERS} -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
