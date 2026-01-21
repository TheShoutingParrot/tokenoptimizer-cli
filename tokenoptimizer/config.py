"""Configuration management for Token Optimizer."""

import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "tokenoptimizer"
CONFIG_FILE = CONFIG_DIR / "config"
ENV_VAR_NAME = "TOKENOPTIMIZER_API_KEY"


def get_config_path() -> Path:
    """Get the path to the config file."""
    return CONFIG_FILE


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_api_key(api_key: str) -> None:
    """Save the API key to the config file."""
    ensure_config_dir()
    CONFIG_FILE.write_text(api_key.strip())
    CONFIG_FILE.chmod(0o600)


def load_api_key() -> str | None:
    """
    Load the API key from environment variable or config file.

    Priority:
    1. Environment variable TOKENOPTIMIZER_API_KEY
    2. Config file ~/.config/tokenoptimizer/config
    """
    env_key = os.environ.get(ENV_VAR_NAME)
    if env_key:
        return env_key.strip()

    if CONFIG_FILE.exists():
        return CONFIG_FILE.read_text().strip()

    return None


def delete_api_key() -> bool:
    """Delete the stored API key. Returns True if deleted, False if not found."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        return True
    return False
