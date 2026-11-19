"""Thin wrappers around the Databricks SQL connector and Files API."""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from databricks.sdk import WorkspaceClient

from databricks import sql
from ingestion.utils.config import DatabricksConfig

logger = logging.getLogger(__name__)


@contextmanager
def sql_connection(config: DatabricksConfig) -> Iterator[Any]:
    """Open a connection to the SQL warehouse and always close it."""
    connection = sql.connect(
        server_hostname=config.host,
        http_path=config.http_path,
        access_token=config.token,
    )
    try:
        yield connection
    finally:
        connection.close()


def run_query(
    connection: Any,
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> list[Any]:
    """Execute a statement; use named parameters (:name) for any values."""
    with connection.cursor() as cursor:
        cursor.execute(statement, dict(parameters) if parameters else None)
        if cursor.description is None:
            return []
        return cursor.fetchall()


def get_workspace_client(config: DatabricksConfig) -> WorkspaceClient:
    """Create a Databricks SDK client (used for Files API / Volumes)."""
    return WorkspaceClient(host=config.workspace_url, token=config.token)
