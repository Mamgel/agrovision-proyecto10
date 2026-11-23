"""Configuracion central de la aplicacion."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./agrovision.db"
    secret_key: str = "cambia_esta_clave_en_produccion_123456"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    model_path: str = "./ai_service/models/best.pt"
    confidence_threshold: float = 0.5
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 10
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    gradio_port: int = 7860
    env: str = "development"


settings = Settings()

# Crear directorios necesarios al inicio
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path("./ai_service/models").mkdir(parents=True, exist_ok=True)
