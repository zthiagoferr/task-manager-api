#!/usr/bin/env bash
set -e

echo "========================================"
echo "  Task Manager API - Inicio Rapido"
echo "========================================"
echo ""

if [ ! -d ".venv" ]; then
    echo "[1/3] Criando ambiente virtual..."
    python3 -m venv .venv
fi

echo "[2/3] Instalando dependencias..."
. .venv/bin/activate
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
    echo "[3/3] Criando arquivo .env..."
    cp .env.example .env
else
    echo "[3/3] Arquivo .env ja existe"
fi

echo ""
echo "========================================"
echo "  Servidor iniciando..."
echo "  API:       http://localhost:8000"
echo "  Swagger:   http://localhost:8000/docs"
echo "  Health:    http://localhost:8000/health"
echo "========================================"
echo ""

fuser -k 8000/tcp 2>/dev/null || true

echo "Executando migracoes..."
alembic upgrade head

echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
