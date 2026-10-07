"""Central application configuration using Pydantic Settings."""
import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # System parameters
    APP_NAME: str = "QuantAI-PaperTrader"
    DEBUG: bool = False
    DATA_DIR: Path = Field(default_factory=lambda: BASE_DIR / "data")
    EXPERIMENTS_DIR: Path = Field(default_factory=lambda: BASE_DIR / "experiments")
    DB_PATH: Path = Field(default_factory=lambda: BASE_DIR / "data" / "experiments.db")

    # Safety constraint: MUST ALWAYS BE TRUE
    PAPER_TRADING_ONLY: bool = True
    ALLOW_REAL_BROKER: bool = False

    # Default execution settings
    DEFAULT_INITIAL_CASH: float = 100000.0  # ₹ or $ depending on market
    DEFAULT_COMMISSION_BPS: float = 3.0     # 3 bps (0.0003)
    DEFAULT_SLIPPAGE_BPS: float = 1.0       # 1 bps (0.0001)

    # Data engine defaults
    DEFAULT_MARKET: Literal["INDIAN_EQUITY", "INDIAN_INDEX", "FOREX", "CRYPTO", "GOLD"] = "INDIAN_EQUITY"
    DEFAULT_DATA_MODE: Literal["HISTORICAL", "LIVE_PAPER", "REPLAY", "DEMO"] = "HISTORICAL"
    DEFAULT_TIMEFRAME: str = "1d"

    # LLM settings
    LLM_PROVIDER: Literal["ollama", "gemini", "openrouter"] = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemini-2.5-flash"
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_RETRIES: int = 3

    # Experiment loop
    DEFAULT_MAX_EXPERIMENTS: int = 10

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
