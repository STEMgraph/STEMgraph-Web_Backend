FROM python:3.11-slim

WORKDIR /app

# Installiere SQLite3 für Debugging
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app
RUN mkdir -p /graph-db/repos /graph-db/templates
COPY ./src/ld-*.json /graph-db/templates
VOLUME ["/graph-db"]

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
