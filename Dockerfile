FROM python:3.11-slim

# -------------------------
# System dependencies
# -------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------
# App directory
# -------------------------
WORKDIR /app

# -------------------------
# Python dependencies
# -------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# Application code
# -------------------------
COPY . .

# -------------------------
# Environment
# -------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# -------------------------
# Start command
# - Run Alembic
# - Then start FastAPI
# -------------------------
CMD alembic upgrade head && \
    uvicorn backend.app.main:app \
