.PHONY: help install run test clean docker-up docker-down

help:
	@echo "Comandos disponiveis:"
	@echo ""
	@echo "  make install     - Instalar dependencias"
	@echo "  make run         - Rodar servidor em desenvolvimento"
	@echo "  make gui         - Abrir aplicativo desktop"
	@echo "  make test        - Rodar todos os testes"
	@echo "  make clean       - Limpar banco, cache e arquivos temporarios"
	@echo "  make docker-up   - Subir com Docker Compose"
	@echo "  make docker-down - Parar containers Docker"
	@echo ""

install:
	@echo "[1/1] Instalando dependencias..."
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	@echo "Pronto! Agora configure seu .env e rode: make run"

run:
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@fuser -k 8000/tcp 2>/dev/null || true
	@echo "Executando migracoes..."
	. .venv/bin/activate && alembic upgrade head
	@echo ""
	@echo "Iniciando servidor em http://localhost:8000"
	@echo "Swagger em http://localhost:8000/docs"
	@echo ""
	. .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	. .venv/bin/activate && pytest tests/ -v

gui:
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "Servidor nao esta rodando. Inicie com: make run"; \
		exit 1; \
	fi
	. .venv/bin/activate && python -m desktop_client.app

clean:
	@echo "Limpando banco de dados..."
	rm -f task_manager.db
	@echo "Limpando cache Python..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	@echo "Limpo."

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
