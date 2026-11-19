"""Verify Databricks connectivity end to end.

Checks: SQL warehouse, Unity Catalog schemas, Volume upload (Files API),
and COPY INTO idempotency. Run from the project root:

    python -m scripts.test_connection
"""

from __future__ import annotations

import io
import logging
from typing import Any

from databricks.sdk import WorkspaceClient

from ingestion.utils.config import DatabricksConfig
from ingestion.utils.databricks_client import (
    get_workspace_client,
    run_query,
    sql_connection,
)

logger = logging.getLogger("connection_test")

EXPECTED_SCHEMAS = {"bronze", "silver", "gold", "audit"}
VOLUME_DIR = "/Volumes/retailpulse/bronze/landing/_connectivity_test"
FILE_PATH = f"{VOLUME_DIR}/hello.csv"
TEST_TABLE = "retailpulse.audit._connectivity_test"
CSV_CONTENT = b"id,note\n1,hello\n2,world\n"


def _copy_into(connection: Any) -> dict[str, Any]:
    # The path is a constant defined above, not user input.
    rows = run_query(
        connection,
        f"""
        COPY INTO {TEST_TABLE}
        FROM '{VOLUME_DIR}/'
        FILEFORMAT = CSV
        FORMAT_OPTIONS ('header' = 'true')
        """,
    )
    return rows[0].asDict() if rows else {}


def _run_checks(connection: Any, client: WorkspaceClient) -> None:
    user, catalog = run_query(connection, "SELECT current_user(), current_catalog()")[0]
    logger.info("1/5 SQL warehouse reachable (user=%s, default catalog=%s)", user, catalog)

    schemas = {row[0] for row in run_query(connection, "SHOW SCHEMAS IN retailpulse")}
    missing = EXPECTED_SCHEMAS - schemas
    if missing:
        raise RuntimeError(f"Missing schemas in retailpulse: {sorted(missing)}")
    logger.info("2/5 Schemas present: %s", sorted(EXPECTED_SCHEMAS))

    client.files.create_directory(VOLUME_DIR)
    client.files.upload(FILE_PATH, io.BytesIO(CSV_CONTENT), overwrite=True)
    logger.info("3/5 Uploaded test file to %s", FILE_PATH)

    run_query(connection, f"CREATE OR REPLACE TABLE {TEST_TABLE} (id STRING, note STRING)")
    first = _copy_into(connection)
    logger.info("4/5 COPY INTO first run: %s", first)
    if first.get("num_inserted_rows") != 2:
        raise RuntimeError(f"Expected 2 inserted rows on first COPY INTO, got {first}")

    second = _copy_into(connection)
    logger.info("5/5 COPY INTO second run (must insert 0): %s", second)
    if second.get("num_inserted_rows") != 0:
        raise RuntimeError(f"COPY INTO was not idempotent: {second}")


def _cleanup(connection: Any, client: WorkspaceClient) -> None:
    try:
        run_query(connection, f"DROP TABLE IF EXISTS {TEST_TABLE}")
        client.files.delete(FILE_PATH)
        client.files.delete_directory(VOLUME_DIR)
        logger.info("Cleanup done")
    except Exception:  # noqa: BLE001 - cleanup must never mask the real error
        logger.warning("Cleanup incomplete; remove %s manually if needed", VOLUME_DIR)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = DatabricksConfig.from_env()
    client = get_workspace_client(config)
    try:
        with sql_connection(config) as connection:
            try:
                _run_checks(connection, client)
            finally:
                _cleanup(connection, client)
    except Exception:
        logger.exception("Connectivity test FAILED")
        return 1
    logger.info("All connectivity checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
