# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:latest AS uv_setup
FROM python:3.12-slim AS builder

COPY --from=uv_setup /uv /uvx /bin/
WORKDIR /app

# This forces uv to put the venv exactly here
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy metadata
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

# Copy the venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# CRITICAL: This is the "magic" that makes the container use the venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Now 'python' and 'pip' will point to the venv versions
CMD ["python", "bot.py"]
