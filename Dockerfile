FROM python:3.11-slim

WORKDIR /app
COPY ./bin/main.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /graph-db/repos /graph-db/templates /graph-db/.secrets
COPY ./bin/ld-*.json /graph-db/templates
COPY ./secrets/github.pat /graph-db/.secrets
VOLUME ["/graph-db"]

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
