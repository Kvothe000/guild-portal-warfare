FROM python:3.11-slim

WORKDIR /app

# Instalar dependências de sistema (para o psycopg2) e utilitários
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

# Copiar requirements antes para cache de build do Docker
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary alembic

COPY . .

# Expõe a porta que o Render costuma usar ou 8000 default
EXPOSE 8000

# Script de entrada para rodar migrations e depois inicializar o servidor
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
