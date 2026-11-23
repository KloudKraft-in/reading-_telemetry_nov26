FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir flask prometheus_client newrelic gunicorn
COPY app.py loadgen.py ./
