"""
momus404 — app.core.config
Centralized, validated environment configuration using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "MOMUS404"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DESCRIPTION: str = "Hybrid Edge-Cloud Autonomous QA Platform"

    # Modes (1 = simulate / mock, 0 = real)
    MOCK_LLM: bool = True
    MOCK_MCP: bool = True
    MOCK_LAYA: bool = True
    MOCK_VAULT: bool = True

    # Cloud LLMs
    HERMES_BASE_URL: str = "https://openrouter.ai/api/v1"
    HERMES_API_KEY: str = ""
    HERMES_MODEL: str = "nousresearch/hermes-3-llama-3.1-405b"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Playwright MCP
    MCP_TRANSPORT: str = "stdio"  # "stdio" | "http"
    MCP_COMMAND: str = "npx @playwright/mcp@latest --headless"
    MCP_HTTP_URL: str = ""

    # Laya Edge Judge (NVIDIA Quadro P1000) - Legacy / fallback
    LAYA_WEIGHTS_PATH: str = "weights/laya-421m-fp16.pt"
    LAYA_DEVICE: str = "cuda:0"
    LAYA_MAX_LATENCY_MS: int = 50

    # Jev Autonomous Decision & Intent Engine
    USE_JEV: bool = True
    JEV_API_KEY: str = ""
    JEV_ENDPOINT: str = "https://api.jev.ai/v1"

    # Orchestration
    MAX_CONCURRENT_TESTS: int = 2
    MAX_HEAL_ATTEMPTS: int = 2
    STEP_TIMEOUT_S: int = 30
    ARTIFACT_RETENTION_HOURS: int = 24

    # Security & Vault
    VAULT_FERNET_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # File storage limits
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    SPECS_DIR: Path = STORAGE_DIR / "specs"
    REPORTS_DIR: Path = STORAGE_DIR / "reports"
    ARTIFACTS_DIR: Path = STORAGE_DIR / "artifacts"
    WEIGHTS_DIR: Path = BASE_DIR / "weights"

    def ensure_directories(self) -> None:
        """Create required persistence directories."""
        for p in (self.SPECS_DIR, self.REPORTS_DIR, self.ARTIFACTS_DIR, self.WEIGHTS_DIR):
            p.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
