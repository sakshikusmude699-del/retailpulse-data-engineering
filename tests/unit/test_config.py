import pytest

from ingestion.utils.config import ConfigError, DatabricksConfig

VARS = ("DATABRICKS_HOST", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN", "DATABRICKS_CATALOG")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in VARS:
        monkeypatch.delenv(name, raising=False)


def _set_valid_env(monkeypatch):
    monkeypatch.setenv("DATABRICKS_HOST", "https://example.cloud.databricks.com/")
    monkeypatch.setenv("DATABRICKS_HTTP_PATH", "/sql/1.0/warehouses/abc123")
    monkeypatch.setenv("DATABRICKS_TOKEN", "dapi-test-token")


def test_missing_variables_raise():
    with pytest.raises(ConfigError, match="DATABRICKS_HOST"):
        DatabricksConfig.from_env(load_env_file=False)


def test_placeholder_values_are_rejected(monkeypatch):
    _set_valid_env(monkeypatch)
    monkeypatch.setenv("DATABRICKS_TOKEN", "your_personal_access_token")
    with pytest.raises(ConfigError, match="Placeholder"):
        DatabricksConfig.from_env(load_env_file=False)


def test_host_is_normalised(monkeypatch):
    _set_valid_env(monkeypatch)
    config = DatabricksConfig.from_env(load_env_file=False)
    assert config.host == "example.cloud.databricks.com"
    assert config.workspace_url == "https://example.cloud.databricks.com"
    assert config.catalog == "retailpulse"


def test_token_is_hidden_from_repr(monkeypatch):
    _set_valid_env(monkeypatch)
    config = DatabricksConfig.from_env(load_env_file=False)
    assert "dapi-test-token" not in repr(config)
