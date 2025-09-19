# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ROOT_PATH=/dbgen

WORKDIR /app

# System deps (optional): ca-certificates
RUN apt-get update -y && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]

