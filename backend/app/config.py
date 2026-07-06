from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/antiraging"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM & Embeddings
    gemini_api_key: str = ""
    groq_api_key: str = ""
    
    @property
    def gemini_keys(self) -> list[str]:
        raw_keys = self.gemini_api_key.strip('"').strip("'")
        return [k.strip() for k in raw_keys.split(",") if k.strip()]

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""

    # Auth
    jwt_secret: str = "super_secret_jwt_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440
    
    # CORS Configuration
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
