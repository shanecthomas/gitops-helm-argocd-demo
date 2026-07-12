# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage — non-root, minimal image
FROM python:3.12-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash svc_api
WORKDIR /home/svc_api/app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/svc_api/.local

# Copy application
COPY --chown=svc_api:svc_api app.py .

# Ensure scripts in .local are usable
ENV PATH=/home/svc_api/.local/bin:$PATH

# Switch to non-root user
USER svc_api

# Expose port
EXPOSE 5050

# Health check — used by Docker and Kubernetes liveness probes
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5050/health')"

# Run with gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "--timeout", "30", "app:app"]
