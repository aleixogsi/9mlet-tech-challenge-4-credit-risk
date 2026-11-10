FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY reports/ ./reports/
COPY logs/ ./logs/

RUN pip install --no-cache-dir \
    "pandas>=2.2" \
    "numpy>=1.26" \
    "pyarrow>=15.0" \
    "prometheus-client>=0.20" \
    "pyyaml>=6.0" \
    && pip install --no-cache-dir --no-deps .

EXPOSE 8000

CMD ["python", "scripts/monitor.py", "--serve", "--host", "0.0.0.0", "--port", "8000"]
