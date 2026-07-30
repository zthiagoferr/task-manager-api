import requests

BASE_URL = "http://localhost:8000/api/v1"
REQUEST_TIMEOUT = 10


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

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        url = f"{self.base_url}{path}"
        try:
            return requests.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Servidor indisponivel. Certifique-se de que 'make run' esta rodando em outro terminal."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                "Tempo de conexao esgotado. O servidor pode estar sobrecarregado."
            )

    def register(self, email: str, username: str, password: str) -> dict:
        resp = self._request(
            "POST", "/auth/register",
            json={"email": email, "username": username, "password": password},
        )
        return self._handle_response(resp)

    def login(self, email: str, password: str) -> dict:
        resp = self._request(
            "POST", "/auth/login",
            json={"email": email, "password": password},
        )
        data = self._handle_response(resp)
        token = data.get("access_token")
        if token:
            self.token = token
            try:
                user = self._get_me()
                self.is_admin = user.get("is_admin", False)
            except RuntimeError:
                self.token = None
                self.is_admin = False
                raise
        return data

    def _get_me(self) -> dict:
        resp = self._request(
            "GET", "/auth/me",
            headers=self._headers(),
        )
        return self._handle_response(resp)

    def list_tasks(self, status: str | None = None) -> list[dict]:
        params = {}
        if status:
            params["status_filter"] = status
        resp = self._request(
            "GET", "/tasks/",
            headers=self._headers(),
            params=params,
        )
        return self._handle_response(resp)

    def create_task(self, title: str, description: str = "", status: str = "pending") -> dict:
        resp = self._request(
            "POST", "/tasks/",
            headers=self._headers(),
            json={"title": title, "description": description, "status": status},
        )
        return self._handle_response(resp)

    def update_task(self, task_id: int, **kwargs) -> dict:
        resp = self._request(
            "PUT", f"/tasks/{task_id}",
            headers=self._headers(),
            json=kwargs,
        )
        return self._handle_response(resp)

    def delete_task(self, task_id: int) -> None:
        resp = self._request(
            "DELETE", f"/tasks/{task_id}",
            headers=self._headers(),
        )
        self._handle_response(resp)

    def list_users(self) -> list[dict]:
        resp = self._request(
            "GET", "/admin/users",
            headers=self._headers(),
        )
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp: requests.Response) -> dict:
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", "Erro desconhecido")
            except requests.exceptions.JSONDecodeError:
                detail = f"Erro HTTP {resp.status_code}"
            raise RuntimeError(detail)
        if resp.status_code == 204:
            return {}
        return resp.json()
