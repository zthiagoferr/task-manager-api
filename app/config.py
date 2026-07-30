from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./task_manager.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_EMAIL: str = ""
    ADMIN_USERNAME: str = "Admin"
    ADMIN_PASSWORD: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def secret_key_validated(self) -> str:
        if self.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY padrão detectada. Defina uma chave secreta no .env."
            )
        return self.SECRET_KEY


settings = Settings()
