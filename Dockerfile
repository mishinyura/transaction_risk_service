FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update -y && \
    apt-get install -y --no-install-recommends curl libpq-dev gcc && \
    pip install --no-cache-dir --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /opt/app

USER appuser

EXPOSE 8000

CMD ["python", "runner.py"]