from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    models_dir: Path = REPO_ROOT / "models"
    output_dir: Path = REPO_ROOT / "output"
    temp_dir: Path = REPO_ROOT / "temp"
    history_file: Path = REPO_ROOT / "backend" / "data" / "history.json"

    cookies_file: Path | None = None
    model_size: str = "auto"
    device: str = "auto"
    compute_type: str = "auto"

    cors_origins: list[str] = ["http://localhost:5173"]
    max_history_entries: int = 50

    def ensure_dirs(self) -> None:
        for path in (self.models_dir, self.output_dir, self.temp_dir, self.history_file.parent):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
