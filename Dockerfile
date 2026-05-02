FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Sao_Paulo

RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs

RUN echo "00 4 * * * root cd /app && /usr/local/bin/python /app/app.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/backfill && \
    echo "00 8 * * * root cd /app && /usr/local/bin/python /app/app.py >> /app/logs/cron.log 2>&1" >> /etc/cron.d/backfill && \
    echo "" >> /etc/cron.d/backfill && \
    chmod 0644 /etc/cron.d/backfill

CMD ["sh", "-c", "env >> /etc/environment && cron -f"]
