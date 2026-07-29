import requests

BASE_URL = "http://localhost:8000/api/v1"


class TaskAPIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: str | None = None
        self.is_admin: bool = False

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def register(self, email: str, username: str, password: str) -> dict:
        resp = requests.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "username": username, "password": password},
        )
        return self._handle_response(resp)

    def login(self, email: str, password: str) -> dict:
        resp = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
        )
        data = self._handle_response(resp)
        self.token = data.get("access_token")
        if self.token:
            user = self._get_me()
            self.is_admin = user.get("is_admin", False)
        return data

    def _get_me(self) -> dict:
        resp = requests.get(
            f"{self.base_url}/auth/me",
            headers=self._headers(),
        )
        return self._handle_response(resp)

    def list_tasks(self, status: str | None = None) -> list[dict]:
        params = {}
        if status:
            params["status_filter"] = status
        resp = requests.get(
            f"{self.base_url}/tasks/",
            headers=self._headers(),
            params=params,
        )
        return self._handle_response(resp)

    def create_task(self, title: str, description: str = "", status: str = "pending") -> dict:
        resp = requests.post(
            f"{self.base_url}/tasks/",
            headers=self._headers(),
            json={"title": title, "description": description, "status": status},
        )
        return self._handle_response(resp)

    def update_task(self, task_id: int, **kwargs) -> dict:
        resp = requests.put(
            f"{self.base_url}/tasks/{task_id}",
            headers=self._headers(),
            json=kwargs,
        )
        return self._handle_response(resp)

    def delete_task(self, task_id: int) -> bool:
        resp = requests.delete(
            f"{self.base_url}/tasks/{task_id}",
            headers=self._headers(),
        )
        return resp.status_code == 204

    def list_users(self) -> list[dict]:
        resp = requests.get(
            f"{self.base_url}/admin/users",
            headers=self._headers(),
        )
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp: requests.Response) -> dict:
        if resp.status_code >= 400:
            detail = resp.json().get("detail", "Erro desconhecido")
            raise RuntimeError(detail)
        return resp.json()
