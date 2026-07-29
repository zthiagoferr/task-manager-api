# Task Manager API

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-14%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

API REST para gerenciamento de tarefas com autenticacao JWT, documentacao automatica e containerizacao.

---

## Inicio Rapido

Clone o repositorio e escolha uma das opcoes abaixo:

### Opcao 1: Script automatico (sem Docker)

```bash
./run.sh
```

O script faz tudo sozinho: cria o ambiente virtual, instala dependencias e sobe o servidor.

### Opcao 2: Make

```bash
make install   # instalar dependencias (primeira vez)
make run       # iniciar servidor
```

### Opcao 3: Docker

```bash
docker compose up -d
```

---

Depois de iniciar, acesse:

| Recurso | URL |
|---|---|
| **Swagger** (testar endpoints) | http://localhost:8000/docs |
| **Health check** | http://localhost:8000/health |

---

## Endpoints

### Autenticacao

| Metodo | Rota | Descricao |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Criar usuario |
| `POST` | `/api/v1/auth/login` | Login (retorna token JWT) |

### Tarefas (requer autenticacao)

| Metodo | Rota | Descricao |
|---|---|---|
| `POST` | `/api/v1/tasks/` | Criar tarefa |
| `GET` | `/api/v1/tasks/` | Listar tarefas |
| `GET` | `/api/v1/tasks/{id}` | Buscar por ID |
| `PUT` | `/api/v1/tasks/{id}` | Atualizar tarefa |
| `DELETE` | `/api/v1/tasks/{id}` | Deletar tarefa |

---

## Testando com cURL

```bash
# Registrar usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","username":"joao","password":"123456"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"123456"}'

# Criar tarefa (substitua <TOKEN> pelo token recebido no login)
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"title":"Estudar Python","status":"pending"}'

# Listar tarefas
curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Comandos Uteis

```bash
make help       # lista todos os comandos
make test       # roda os testes
make clean      # limpa banco e cache
make docker-up  # sobe com Docker
```

---

## Stack

| Tecnologia | Uso |
|---|---|
| FastAPI | Framework web |
| SQLAlchemy | ORM assincrono |
| SQLite | Banco de dados |
| Alembic | Migracoes |
| JWT (python-jose) | Autenticacao |
| BCrypt (passlib) | Hash de senhas |
| Pydantic | Validacao de dados |
| Docker | Containerizacao |

---

## Arquitetura

```
app/
├── main.py          # Ponto de entrada
├── config.py        # Configuracoes
├── database.py      # Conexao com banco
├── models/          # Modelos SQLAlchemy
├── schemas/         # Validacao Pydantic
├── routers/         # Endpoints HTTP
├── services/        # Logica de negocios
└── dependencies/    # Injecao de dependencias
```

Documentacao completa em [ARQUITETURA.md](ARQUITETURA.md).

---

## Autor

**Thiago Ferreira de Oliveira**

- GitHub: [@zthiagoferr](https://github.com/zthiagoferr)
- GitLab: [@thia80.ferreira](https://gitlab.com/thia80.ferreira)
- Email: contato.thiagofo@icloud.com
