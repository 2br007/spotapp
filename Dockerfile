FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY scripts ./scripts
COPY static ./static
COPY seed_data.py spotapp.py ./

EXPOSE 8000

CMD ["sh", "-c", "python scripts/init_db.py && uvicorn spotapp:app --host 0.0.0.0 --port 8000"]
