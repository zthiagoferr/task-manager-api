import pytest


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


async def _register_and_login(client):
    await client.post("/api/v1/auth/register", json={
        "email": "taskuser@example.com",
        "username": "taskuser",
        "password": "secret123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "taskuser@example.com",
        "password": "secret123",
    })
    return resp.json()["access_token"]


class TestTasks:
    @pytest.mark.asyncio
    async def test_create_task(self, client):
        token = await _register_and_login(client)
        payload = {
            "title": "Minha primeira tarefa",
            "description": "Descrição da tarefa",
            "status": "pending",
        }
        response = await client.post(
            "/api/v1/tasks/",
            json=payload,
            headers=_auth_headers(token),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["status"] == "pending"
        assert data["owner_id"] is not None

    @pytest.mark.asyncio
    async def test_create_task_without_auth(self, client):
        response = await client.post("/api/v1/tasks/", json={"title": "Tarefa"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_tasks(self, client):
        token = await _register_and_login(client)
        for i in range(3):
            await client.post(
                "/api/v1/tasks/",
                json={"title": f"Tarefa {i}"},
                headers=_auth_headers(token),
            )
        response = await client.get("/api/v1/tasks/", headers=_auth_headers(token))
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_filter_tasks_by_status(self, client):
        token = await _register_and_login(client)
        await client.post(
            "/api/v1/tasks/",
            json={"title": "Pendente", "status": "pending"},
            headers=_auth_headers(token),
        )
        await client.post(
            "/api/v1/tasks/",
            json={"title": "Concluída", "status": "completed"},
            headers=_auth_headers(token),
        )
        response = await client.get(
            "/api/v1/tasks/?status_filter=completed",
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Concluída"

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, client):
        token = await _register_and_login(client)
        create_resp = await client.post(
            "/api/v1/tasks/",
            json={"title": "Buscar"},
            headers=_auth_headers(token),
        )
        task_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Buscar"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client):
        token = await _register_and_login(client)
        response = await client.get(
            "/api/v1/tasks/9999",
            headers=_auth_headers(token),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(self, client):
        token = await _register_and_login(client)
        create_resp = await client.post(
            "/api/v1/tasks/",
            json={"title": "Original"},
            headers=_auth_headers(token),
        )
        task_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Atualizada", "status": "completed"},
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Atualizada"
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_delete_task(self, client):
        token = await _register_and_login(client)
        create_resp = await client.post(
            "/api/v1/tasks/",
            json={"title": "Deletar"},
            headers=_auth_headers(token),
        )
        task_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=_auth_headers(token),
        )
        assert response.status_code == 204

        get_resp = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=_auth_headers(token),
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_task_isolation(self, client):
        # User 1
        token1 = await _register_and_login(client)

        # Register user 2
        await client.post("/api/v1/auth/register", json={
            "email": "user2@example.com",
            "username": "user2",
            "password": "secret123",
        })
        resp2 = await client.post("/api/v1/auth/login", json={
            "email": "user2@example.com",
            "password": "secret123",
        })
        token2 = resp2.json()["access_token"]

        # User 1 creates a task
        await client.post(
            "/api/v1/tasks/",
            json={"title": "Tarefa do User 1"},
            headers=_auth_headers(token1),
        )

        # User 2 cannot see it
        response = await client.get("/api/v1/tasks/", headers=_auth_headers(token2))
        assert response.status_code == 200
        assert len(response.json()) == 0
