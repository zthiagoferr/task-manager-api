# Task Manager API — Documentacao de Arquitetura

## 1. Visao Geral

Task Manager API e uma API REST para gerenciamento de tarefas pessoais com autenticacao JWT, painel administrativo e app desktop. O sistema permite que usuarios se registrem, facam login, e realizem operacoes CRUD sobre suas proprias tarefas, com isolamento completo de dados entre usuarios.

- **Versao:** 1.0.0
- **Linguagem:** Python 3.12+
- **Licenca:** MIT
- **Autor:** Thiago Ferreira de Oliveira
- **Deploy:** Render (`https://task-manager-a421.onrender.com`)

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
| App Desktop       | CustomTkinter + Requests            | 6.0.0/2.31  |
| Containerizacao   | Docker + Docker Compose             | —         |
| Deploy            | Railway                             | —         |
| Testes            | Pytest + pytest-asyncio + HTTPX     | 9.1.1/1.4.0/0.28.1 |

---

## 3. Arquitetura em Camadas

O projeto segue o padrao **Service Layer** com clara separacao de responsabilidades:

```
Cliente HTTP        App Desktop (CustomTkinter)
    |                       |
    v                       v
[Routers]        — recebem a requisicao, delegam ao Service
    |
    v
[Dependencies]   — injecao de dependencias (auth, admin)
    |
    v
[Services]       — logica de negocio pura
    |
    v
[Models/SQLA]    — acesso a dados via ORM
    |
    v
[Banco: SQLite]  — persistencia (Alembic gerencia migracoes)
```

---

## 4. Estrutura de Diretorios

```
.
├── .env.example                 # Template de variaveis de ambiente
├── .gitignore
├── alembic.ini                  # Configuracao do Alembic
├── ARQUITETURA.md               # Este documento
├── docker-compose.yml
├── Dockerfile
├── LICENSE                      # MIT
├── Makefile                     # make run, make test, make gui, make clean
├── pyproject.toml               # Metadados do projeto
├── railway.json                 # Config do Railway
├── README.md
├── requirements.txt
├── run.sh                       # Script de inicio rapido
├── desktop_client/              # App desktop com CustomTkinter
│   ├── api.py                   # Cliente HTTP da API
│   ├── app.py                   # Interface grafica (login + tarefas + admin)
│   └── run.sh
├── migrations/                  # Migracoes do Alembic
│   ├── env.py
│   └── versions/
│       ├── 870bb6b4a3c8_initial.py
│       └── 2a482e266b91_add_is_admin_to_users.py
├── tests/
│   ├── conftest.py              # Fixtures globais dos testes
│   ├── test_auth.py             # 5 testes de autenticacao
│   └── test_tasks.py            # 9 testes de tarefas
└── app/
    ├── main.py                  # Ponto de entrada FastAPI
    ├── config.py                # Settings carregadas do .env
    ├── database.py              # Engine async, sessao e Base
    ├── seed.py                  # Cria usuario admin no startup
    ├── dependencies/
    │   ├── auth.py              # get_current_user (JWT decode)
    │   └── admin.py             # get_current_admin (verifica is_admin)
    ├── models/
    │   ├── user.py              # Modelo User (com is_admin)
    │   └── task.py              # Modelo Task + enum TaskStatus
    ├── routers/
    │   ├── auth.py              # POST /register, POST /login, GET /me
    │   ├── tasks.py             # CRUD /tasks/
    │   └── admin.py             # GET /admin/users (admin only)
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
│ is_admin (BOOL)  │         │ due_date (NULL)      │
│ created_at       │         │ created_at           │
└──────────────────┘         │ updated_at           │
                             │ owner_id (FK)        │
                             └──────────────────────┘
```

### 5.1 Tabela `users`

| Coluna          | Tipo         | Restricoes                  |
|-----------------|--------------|-----------------------------|
| id              | INTEGER      | PK, INDEX                   |
| email           | VARCHAR(255) | UNIQUE, INDEX, NOT NULL     |
| username        | VARCHAR(100) | UNIQUE, INDEX, NOT NULL     |
| hashed_password | VARCHAR(255) | NOT NULL                    |
| is_admin        | BOOLEAN      | NOT NULL, DEFAULT FALSE     |
| created_at      | DATETIME TZ  | DEFAULT NOW()               |

### 5.2 Tabela `tasks`

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
| GET    | `/me`       | Sim  | Retorna dados do usuario logado   | 200 UserResponse |

### 6.2 Tarefas (`/tasks`)

| Metodo | Rota          | Auth | Descricao                               | Resposta          |
|--------|---------------|------|-----------------------------------------|-------------------|
| POST   | `/`           | Sim  | Cria tarefa                             | 201 TaskResponse  |
| GET    | `/`           | Sim  | Lista tarefas (filtro por status, pag.) | 200 list[TaskResponse] |
| GET    | `/{task_id}`  | Sim  | Busca tarefa por ID                     | 200 TaskResponse  |
| PUT    | `/{task_id}`  | Sim  | Atualiza tarefa                         | 200 TaskResponse  |
| DELETE | `/{task_id}`  | Sim  | Remove tarefa                           | 204 No Content    |

### 6.3 Admin (`/admin`)

| Metodo | Rota     | Auth       | Descricao                    | Resposta            |
|--------|----------|------------|------------------------------|---------------------|
| GET    | `/users` | Sim (admin)| Lista todos os usuarios      | 200 list[UserResponse] |

### 6.4 Sistema

| Metodo | Rota      | Auth | Descricao        | Resposta          |
|--------|-----------|------|------------------|-------------------|
| GET    | `/health` | Nao  | Health check     | 200 {"status":"healthy"} |

### 6.5 Query Parameters (GET `/tasks/`)

| Parametro       | Tipo        | Padrao | Descricao                  |
|-----------------|-------------|--------|----------------------------|
| `status_filter` | TaskStatus? | null   | Filtra por status          |
| `skip`          | int         | 0      | Offset da paginacao        |
| `limit`         | int         | 100    | Limite de itens por pagina |

---

## 7. App Desktop (CustomTkinter)

Interface grafica em `desktop_client/` que consome a API:

| Tela | Funcionalidade |
|---|---|
| **LoginWindow** | Login/registro com feedback visual (pop-up de confirmacao) |
| **MainWindow** | Lista de tarefas em cards coloridos, filtro por status, criar/editar/excluir |
| **TaskDialog** | Formulario de criacao/edicao com botoes de status |
| **AdminPanel** | Lista todos os usuarios (exclusivo para admin) |

Atalhos: `Ctrl+N` nova tarefa, `Ctrl+R` atualizar, `Esc` fechar dialogo.

O cliente detecta se o usuario e admin apos login e mostra o botao "Admin" no header.

---

## 8. Seed de Admin

No startup do servidor, o modulo `app/seed.py` garante que o usuario administrador existe:

- **Email:** `thia80.ferreira@gmail.com`
- **Username:** `Admin`
- **Senha:** `191006`

Se o admin ja existir, apenas atualiza `is_admin = True`. Se nao existir, cria.

---

## 9. Fluxos Principais

### 9.1 Registro com Tratamento de Duplicidade

```
POST /api/v1/auth/register
       |
       v
app.services.auth.register_user()
  ├─ db.add(user)
  ├─ db.commit()
  │    └─ IntegrityError? → rollback → HTTP 409 "Email ou username ja cadastrado"
  └─ db.refresh(user) → UserResponse
```

### 9.2 Autorizacao JWT

```
Header: Authorization: Bearer <token>
       |
       v
app.dependencies.auth.get_current_user()
  ├─ jwt.decode(token, SECRET_KEY, HS256)
  ├─ Extrai user_id do payload
  ├─ Busca User no banco
  └─ Retorna User | HTTP 401
```

### 9.3 Autorizacao Admin

```
app.dependencies.admin.get_current_admin()
  ├─ Chama get_current_user()
  ├─ Verifica user.is_admin
  └─ Retorna User | HTTP 403 "Acesso restrito a administradores"
```

---

## 10. Migracoes (Alembic)

Configuracao em `alembic.ini` (URL sincrona para comandos CLI) e `migrations/env.py` (suporta conexao passada via atributo para o `run_sync` no lifespan do FastAPI).

```bash
alembic upgrade head                          # aplicar migracoes
alembic downgrade -1                          # reverter ultima
alembic revision --autogenerate -m "desc"     # gerar nova migracao
```

Migracoes existentes:
- `870bb6b4a3c8_initial.py` — tabelas `users` e `tasks`
- `2a482e266b91_add_is_admin_to_users.py` — coluna `is_admin` em `users`

---

## 11. Configuracao e Variaveis de Ambiente

| Variavel                    | Padrao                                  | Descricao                         |
|-----------------------------|-----------------------------------------|------------------------------------|
| DATABASE_URL                | sqlite+aiosqlite:///./task_manager.db   | URL de conexao do banco           |
| SECRET_KEY                  | dev-secret-key-change-in-production     | Chave para assinar JWT            |
| ALGORITHM                   | HS256                                   | Algoritmo JWT                     |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30                                      | Tempo de vida do token (minutos)  |

---

## 12. Testes

Suite com **14 testes** automatizados, todos passando sem warnings:

### Autenticacao (5)

| Teste                          | Verifica                                        |
|--------------------------------|--------------------------------------------------|
| `test_register_user`           | Registro com sucesso retorna 201 + dados        |
| `test_register_duplicate_email`| Email duplicado retorna **409 Conflict**         |
| `test_login_success`           | Login com credenciais corretas retorna JWT      |
| `test_login_wrong_password`    | Senha errada retorna 401                         |
| `test_login_nonexistent_user`  | Usuario inexistente retorna 401                  |

### Tarefas (9)

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

---

## 13. Containerizacao e Deploy

### Docker

```bash
docker build -t task-manager-api .
docker run -p 8000:8000 --env-file .env task-manager-api
```

### Docker Compose

```bash
docker compose up -d
```

### Railway

```bash
railway up
```

### Render

Deploy em producao: `https://task-manager-a421.onrender.com`

---

## 14. Decisoes Arquiteturais

### Por que FastAPI?
- Tipagem nativa, documentacao automatica (Swagger), suporte assincrono, validacao com Pydantic.

### Por que SQLite?
- Zero configuracao, suficiente para o escopo, facilmente substituivel por PostgreSQL.

### Por que Service Layer?
- Routers lidam com HTTP, Services com logica de negocio. Testavel e desacoplado.

### Por que JWT?
- Stateless, adequado para APIs REST, python-jose maduro.

### Por que `IntegrityError` no Service?
- Evita race condition entre SELECT e INSERT. O banco e a fonte da verdade.

### Por que CustomTkinter?
- Moderno, tema escuro nativo, facil de usar. Torna a API acessivel para usuarios nao-tecnicos.

---

## 15. Como Rodar

```bash
# Local
make install   # primeira vez
make run       # servidor em http://localhost:8000
make gui       # app desktop
make test      # 14 testes

# Docker
make docker-up
```
