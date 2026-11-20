FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONUNBUFFERED=1
# The service to run is chosen by each compose file, e.g.:
#   command: uvicorn s1_checkout:app --host 0.0.0.0 --port 8081
