# ──────────────────────────────────────────────────────────────────────────────
# Eye Adaptive Lens System — Host (Raspberry Pi / x86-64)
#
# Build:  docker build -t eye-lens-system:latest .
# Run:    docker run --rm --env-file .env eye-lens-system:latest
# ──────────────────────────────────────────────────────────────────────────────

# Use Debian Bookworm slim for a small image that works on Pi 4 (arm64) and
# standard x86-64 CI runners alike.
FROM python:3.11-slim-bookworm AS base

LABEL maintainer="Eye Adaptive Lens System"
LABEL description="Host software for the Eye Adaptive Lens System research prototype"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install OS-level dependencies (serial port access + OpenCV prerequisites)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libglib2.0-dev \
        udev \
    && rm -rf /var/lib/apt/lists/*

# ── Build layer: install Python dependencies ──────────────────────────────────
FROM base AS builder

WORKDIR /build

# Copy dependency manifests first to maximise layer cache reuse
COPY requirements.txt requirements-dev.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Final runtime image ───────────────────────────────────────────────────────
FROM base AS runtime

# Create a non-root user for the application
RUN groupadd --gid 1001 eyeapp && \
    useradd --uid 1001 --gid eyeapp --shell /bin/bash --create-home eyeapp

# Add to dialout group for serial port access
RUN usermod -aG dialout eyeapp

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY --chown=eyeapp:eyeapp . /app

# Create runtime directories
RUN mkdir -p /app/data/sessions /app/logs /app/host/pi/models && \
    chown -R eyeapp:eyeapp /app/data /app/logs /app/host/pi/models

USER eyeapp

# Default environment values (override via .env or docker run --env-file)
ENV LOG_LEVEL=INFO
ENV DATA_DIR=/app/data/sessions
ENV CV_LOG_DIR=/app/logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose log and data directories as volumes for persistence
VOLUME ["/app/data", "/app/logs"]

# Default entrypoint: run the telemetry demo in mock mode
# Override CMD in docker-compose or at runtime for other entry points
CMD ["python", "-m", "host.pi.telemetry_demo", "--mock", "--duration", "30"]
