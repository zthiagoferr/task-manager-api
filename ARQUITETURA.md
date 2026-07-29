# Task Manager API — Documentacao de Arquitetura

## 1. Visao Geral

Task Manager API e uma API REST para gerenciamento de tarefas pessoais com autenticacao JWT. O sistema permite que usuarios se registrem, facam login, e realizem operacoes CRUD sobre suas proprias tarefas, com isolamento completo de dados entre usuarios.

- **Versao:** 1.0.0
- **Linguagem:** Python 3.12+
- **Licenca:** Privada

---

## 2. Stack Tecnologica

| Camada           | Tecnologia                          | Versao    |
|-------------------|-------------------------------------|-----------|
| Framework web     | FastAPI                             | 0.141.1   |
| Servidor ASGI     | Uvicorn                             | 0.52.0    |
| ORM               | SQLAlchemy (modo assincrono)        | 2.0.51    |
| Banco de dados    | SQLite (via aiosqlite)              | 0.22.1    |
| Migracoes         | Alembic                             | 1.18.5    |
| Validacao         | Pydantic v2                         | 2.13.4    |
| Configuracao      | Pydantic-Settings                   | 2.14.2    |
| Autenticacao      | JWT (python-jose) + BCrypt (passlib)| 3.5.0/1.7.4 |
| Containerizacao   | Docker + Docker Compose             | —         |
| Testes            | Pytest + pytest-asyncio + HTTPX     | 9.1.1/1.4.0/0.28.1 |

---

## 3. Arquitetura em Camadas

O projeto segue o padrao **Service Layer** com clara separacao de responsabilidades:

```
Cliente HTTP
    |
    v
[Routers]        — recebem a requisicao, delegam ao Service
    |
    v
[Services]       — logica de negocio pura
    |
    v
[Models/SQLA]    — acesso a dados via ORM
    |
    v
[Banco: SQLite]  — persistencia
```

Camadas transversais:

- **Dependencies** — injecao de dependencias (ex: `get_current_user`)
- **Schemas** — validacao/serializacao com Pydantic
- **Config** — variaveis de ambiente centralizadas

---

## 4. Estrutura de Diretorios

```
.
├── .env.example                 # Template de variaveis de ambiente
├── .gitignore
├── ARQUITETURA.md               # Este documento
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── tests/
│   ├── conftest.py              # Fixtures globais dos testes
│   ├── test_auth.py             # 5 testes de autenticacao
│   └── test_tasks.py            # 9 testes de tarefas
└── app/
    ├── main.py                  # Ponto de entrada FastAPI
    ├── config.py                # Settings carregadas do .env
    ├── database.py              # Engine async, sessao e Base
    ├── dependencies/
    │   └── auth.py              # get_current_user (JWT decode)
    ├── models/
    │   ├── user.py              # Modelo User
    │   └── task.py              # Modelo Task + enum TaskStatus
    ├── routers/
    │   ├── auth.py              # POST /register, POST /login
    │   └── tasks.py             # CRUD /tasks/
    ├── schemas/
    │   ├── user.py              # UserCreate, UserLogin, UserResponse, Token
    │   └── task.py              # TaskCreate, TaskUpdate, TaskResponse
    └── services/
        ├── auth.py              # hash, verify, JWT, register, authenticate
        └── task.py              # CRUD logica de tarefas
```

---

## 5. Modelo de Dados (Entidade-Relacionamento)

```
┌──────────────────┐         ┌──────────────────────┐
│      users       │         │        tasks         │
├──────────────────┤         ├──────────────────────┤
│ id (PK)          │──1:N───>│ id (PK)              │
│ email (UNIQUE)   │         │ title                │
│ username (UNIQUE)│         │ description (NULL)   │
│ hashed_password  │         │ status (ENUM)        │
│ created_at       │         │ due_date (NULL)      │
└──────────────────┘         │ created_at           │
                             │ updated_at           │
                             │ owner_id (FK)        │
                             └──────────────────────┘
```

### 5.1 Detalhes da Tabela `users`

| Coluna          | Tipo         | Restricoes                  |
|-----------------|--------------|-----------------------------|
| id              | INTEGER      | PK, INDEX                   |
| email           | VARCHAR(255) | UNIQUE, INDEX, NOT NULL     |
| username        | VARCHAR(100) | UNIQUE, INDEX, NOT NULL     |
| hashed_password | VARCHAR(255) | NOT NULL                    |
| created_at      | DATETIME TZ  | DEFAULT NOW()               |

### 5.2 Detalhes da Tabela `tasks`

| Coluna       | Tipo         | Restricoes                        |
|--------------|--------------|-----------------------------------|
| id           | INTEGER      | PK, INDEX                         |
| title        | VARCHAR(200) | NOT NULL                          |
| description  | VARCHAR(1000)| NULL                              |
| status       | ENUM         | NOT NULL, DEFAULT 'pending'       |
| due_date     | DATETIME TZ  | NULL                              |
| created_at   | DATETIME TZ  | DEFAULT NOW()                     |
| updated_at   | DATETIME TZ  | DEFAULT NOW(), ON UPDATE NOW()    |
| owner_id     | INTEGER      | FK -> users.id, ON DELETE CASCADE |

### 5.3 Enum `TaskStatus`

| Valor        | Significado        |
|--------------|--------------------|
| `pending`    | Pendente           |
| `in_progress`| Em andamento       |
| `completed`  | Concluida          |

---

## 6. Endpoints da API

Base URL: `/api/v1`

### 6.1 Autenticacao (`/auth`)

| Metodo | Rota        | Auth | Descricao                         | Resposta       |
|--------|-------------|------|-----------------------------------|----------------|
| POST   | `/register` | Nao  | Cria novo usuario                 | 201 UserResponse |
| POST   | `/login`    | Nao  | Autentica e retorna JWT           | 200 Token      |

### 6.2 Tarefas (`/tasks`)

| Metodo | Rota          | Auth | Descricao                               | Resposta          |
|--------|---------------|------|-----------------------------------------|-------------------|
| POST   | `/`           | Sim  | Cria tarefa                             | 201 TaskResponse  |
| GET    | `/`           | Sim  | Lista tarefas (filtro por status, pag.) | 200 list[TaskResponse] |
| GET    | `/{task_id}`  | Sim  | Busca tarefa por ID                     | 200 TaskResponse  |
| PUT    | `/{task_id}`  | Sim  | Atualiza tarefa                         | 200 TaskResponse  |
| DELETE | `/{task_id}`  | Sim  | Remove tarefa                           | 204 No Content    |

### 6.3 Query Parameters (GET `/tasks/`)

| Parametro       | Tipo        | Padrao | Descricao                  |
|-----------------|-------------|--------|----------------------------|
| `status_filter` | TaskStatus? | null   | Filtra por status          |
| `skip`          | int         | 0      | Offset da paginacao        |
| `limit`         | int         | 100    | Limite de itens por pagina |

---

## 7. Fluxos Principais

### 7.1 Registro de Usuario

```
POST /api/v1/auth/register
  { email, username, password }
       |
       v
router.auth.register()
       |
       v
services.auth.register_user()
  ├─ User(email, username, hashed_password)
  ├─ db.add(user)
  ├─ db.commit()
  │    └─ IntegrityError? → rollback → HTTP 409 "Email ou username ja cadastrado"
  └─ db.refresh(user) → UserResponse
```

### 7.2 Login e Autenticacao

```
POST /api/v1/auth/login
  { email, password }
       |
       v
router.auth.login()
       |
       v
services.auth.authenticate_user()
  ├─ SELECT user WHERE email = ?
  ├─ verify_password(password, hashed)
  └─ User | None
       |
       v
services.auth.create_access_token({ user_id })
  └─ JWT com expiracao (HS256)
       |
       v
Resposta: { access_token, token_type: "bearer" }
```

### 7.3 Autorizacao (Middleware)

Toda rota protegida usa a dependencia `get_current_user`:

```
Header: Authorization: Bearer <token>
       |
       v
dependencies.auth.get_current_user()
  ├─ Extrai token do header (OAuth2PasswordBearer)
  ├─ jwt.decode(token, SECRET_KEY, HS256)
  ├─ Extrai user_id do payload
  ├─ Busca User no banco
  └─ Retorna User | HTTP 401
```

### 7.4 CRUD de Tarefas

```
Criar:
  POST /api/v1/tasks/
  → task_service.create_task(db, owner_id, task_data)
  → Task(..., owner_id=current_user.id)

Listar:
  GET /api/v1/tasks/?status_filter=pending&skip=0&limit=10
  → task_service.get_tasks(db, owner_id, status, skip, limit)
  → SELECT ... WHERE owner_id = ? [AND status = ?] ORDER BY created_at DESC

Buscar / Atualizar / Deletar:
  → task_service.get_task_by_id(db, task_id, owner_id)
  → WHERE id = ? AND owner_id = ?
  → Se nao encontrado: HTTP 404
```

### 7.5 Isolamento de Dados

Toda query de tarefas inclui `WHERE owner_id = current_user.id`. Um usuario **nunca** consegue acessar tarefas de outro usuario, mesmo conhecendo o ID da tarefa — a consulta sempre cruza `id` + `owner_id`.

---

## 8. Configuracao e Variaveis de Ambiente

Arquivo `.env` (baseado em `.env.example`):

```env
DATABASE_URL=sqlite+aiosqlite:///./task_manager.db
SECRET_KEY=change-me-to-a-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

| Variavel                    | Padrao                                  | Descricao                         |
|-----------------------------|-----------------------------------------|------------------------------------|
| DATABASE_URL                | sqlite+aiosqlite:///./task_manager.db   | URL de conexao do banco           |
| SECRET_KEY                  | dev-secret-key-change-in-production     | Chave para assinar JWT            |
| ALGORITHM                   | HS256                                   | Algoritmo JWT                     |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30                                      | Tempo de vida do token (minutos)  |

---

## 9. Testes

Suite com **14 testes** automatizados, todos passando sem warnings:

### Testes de Autenticacao (5)

| Teste                          | Verifica                                        |
|--------------------------------|--------------------------------------------------|
| `test_register_user`           | Registro com sucesso retorna 201 + dados        |
| `test_register_duplicate_email`| Email duplicado retorna **409 Conflict**         |
| `test_login_success`           | Login com credenciais corretas retorna JWT      |
| `test_login_wrong_password`    | Senha errada retorna 401                         |
| `test_login_nonexistent_user`  | Usuario inexistente retorna 401                  |

### Testes de Tarefas (9)

| Teste                         | Verifica                                         |
|-------------------------------|---------------------------------------------------|
| `test_create_task`            | Criacao com sucesso retorna 201                   |
| `test_create_task_without_auth`| Sem token retorna 401                             |
| `test_list_tasks`             | Listagem retorna tarefas do usuario               |
| `test_filter_tasks_by_status`  | Filtro por status funciona                        |
| `test_get_task_by_id`         | Busca por ID funciona                             |
| `test_get_task_not_found`     | ID inexistente retorna 404                        |
| `test_update_task`            | Atualizacao funciona                              |
| `test_delete_task`            | Delecao retorna 204 + item some da listagem       |
| `test_task_isolation`         | Usuario A nao ve tarefas do usuario B             |

### Estrategia de Testes

- Banco SQLite em memoria (`sqlite+aiosqlite:///:memory:`)
- Tabelas criadas/destruidas a cada teste (`setup_db` fixture autouse)
- Sessao de banco sobrescrita via `dependency_overrides`
- Cliente HTTP assincrono (`httpx.AsyncClient` com `ASGITransport`)

---

## 10. Containerizacao

### 10.1 Docker

```bash
# Build
docker build -t task-manager-api .

# Run
docker run -p 8000:8000 --env-file .env task-manager-api
```

### 10.2 Docker Compose

```bash
docker-compose up -d
```

Servico exposto em `http://localhost:8000`, banco SQLite persistido via volume.

---

## 11. Decisoes Arquiteturais

### 11.1 Por que FastAPI?

- Tipagem nativa com Python type hints
- Documentacao automatica (Swagger/OpenAPI)
- Suporte assincrono nativo (`async/await`)
- Validacao com Pydantic integrada
- Ecossistema maduro para APIs REST

### 11.2 Por que SQLite?

- Zero configuracao para desenvolvimento local
- Suficiente para o escopo do projeto (single-user isolation)
- Facilmente substituivel por PostgreSQL com SQLAlchemy (basta trocar a URL)

### 11.3 Por que Service Layer?

- **Routers** so lidam com HTTP (request/response, status codes)
- **Services** contem logica de negocio pura, testavel isoladamente
- Facilita troca de framework web ou adicao de outros entrypoints (CLI, GraphQL, gRPC)

### 11.4 Por que JWT?

- Stateless — nao requer sessao no servidor
- Adequado para APIs REST
- python-jose e maduro e bem testado

### 11.5 Por que `IntegrityError` no Service (e nao pre-query)?

Optou-se por tratar a excecao de constraint do banco em vez de fazer uma query previa (`SELECT ... WHERE email = ?`) porque:

- Evita race condition entre SELECT e INSERT
- O banco e a fonte da verdade para unicidade
- O rollback garante consistencia transacional

---

## 12. Como Rodar

### 12.1 Local

```bash
# Criar virtualenv
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env

# Rodar servidor
uvicorn app.main:app --reload
```

API disponivel em `http://localhost:8000`  
Swagger em `http://localhost:8000/docs`

### 12.2 Testes

```bash
pytest tests/ -v
```

---

## 13. Possiveis Evolucoes

| Item                      | Descricao                                                 |
|---------------------------|-----------------------------------------------------------|
| Refresh token             | Implementar rotacao de token com refresh token            |
| Paginacao com metadados   | Retornar `total`, `page`, `pages` no header/body          |
| Ordenacao flexivel        | Query param `order_by` com campos e direcao               |
| Migracoes com Alembic     | Configurar `alembic.ini` e `migrations/`                  |
| CORS                     | Middleware para permitir frontend externo                  |
| Health check             | Endpoint `GET /health` para orquestradores                 |
| Logging                  | Configurar logging estruturado (structlog/loguru)          |
| Testes de integracao     | Adicionar cobertura para servicos isolados                 |
| CI/CD                    | Pipeline com GitHub Actions rodando lint + testes          |
