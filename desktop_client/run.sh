#!/usr/bin/env bash
set -e

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Erro: O servidor nao esta rodando."
    echo "Inicie primeiro com: make run"
    echo ""
    echo "Em outro terminal, execute: make run"
    echo "Depois volte aqui e execute: make gui"
    exit 1
fi

. .venv/bin/activate
python -m desktop_client.app
