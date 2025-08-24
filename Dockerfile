FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Use prebuilt index if present; only build if missing
RUN if [ -f data/index/faiss.index ] && [ -f data/index/docs.json ] && [ -f data/index/bm25.pkl ]; then \
      echo "Using prebuilt index in data/index"; \
    else \
      echo "Index not found, building..." && python -m ingestion.build_index; \
    fi

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]