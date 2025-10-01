FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip \
    && if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . .

ENV APP_MODULE=app.main:app
ENV APP_PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn ${APP_MODULE:-app.main:app} --host 0.0.0.0 --port ${APP_PORT:-8000}"]
