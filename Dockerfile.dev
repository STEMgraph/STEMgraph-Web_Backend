FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bin/main.py /app
RUN mkdir -p /graph-db/repos /graph-db/templates
COPY ./bin/ld-*.json /graph-db/templates
VOLUME ["/graph-db"]

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
