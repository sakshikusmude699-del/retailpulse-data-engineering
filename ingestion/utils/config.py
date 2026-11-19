"""Load and validate Databricks connection settings from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

REQUIRED_VARS = (
    "DATABRICKS_HOST",
    "DATABRICKS_HTTP_PATH",
    "DATABRICKS_TOKEN",
)
PLACEHOLDER_PREFIX = "your_"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or still a placeholder."""


@dataclass(frozen=True)
class DatabricksConfig:
    """Connection settings for the Databricks workspace and SQL warehouse."""

    host: str
    http_path: str
    token: str = field(repr=False)
    catalog: str = "retailpulse"

    @property
    def workspace_url(self) -> str:
        return f"https://{self.host}"

    @classmethod
    def from_env(cls, load_env_file: bool = True) -> DatabricksConfig:
        """Build the config from environment variables (and `.env` if present)."""
        if load_env_file:
            load_dotenv()

        missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
        if missing:
            raise ConfigError(
                f"Missing environment variables: {', '.join(missing)}. "
                "Copy .env.example to .env and fill in your values."
            )

        placeholders = [
            name
            for name in REQUIRED_VARS
            if os.environ[name].strip().lower().startswith(PLACEHOLDER_PREFIX)
        ]
        if placeholders:
            raise ConfigError(f"Placeholder values still set for: {', '.join(placeholders)}.")

        host = os.environ["DATABRICKS_HOST"].strip()
        host = host.removeprefix("https://").removeprefix("http://").rstrip("/")

        return cls(
            host=host,
            http_path=os.environ["DATABRICKS_HTTP_PATH"].strip(),
            token=os.environ["DATABRICKS_TOKEN"].strip(),
            catalog=os.getenv("DATABRICKS_CATALOG", "retailpulse").strip(),
        )
