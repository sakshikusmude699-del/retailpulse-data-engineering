"""Generate the initial full-load snapshot files into data/landing.

python -m scripts.generate_initial_load
python -m scripts.generate_initial_load --output data/landing --batch-id B000000
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from ingestion.generators.master_data import (
    generate_customers,
    generate_products,
    generate_stores,
)
from ingestion.generators.settings import GenerationSettings
from ingestion.utils.files import landing_path, validate_batch_id, write_csv

logger = logging.getLogger("generate_initial_load")

# Step 3.2 adds the transactional entities to this registry.
GENERATORS: dict[str, Callable[[GenerationSettings], pd.DataFrame]] = {
    "stores": generate_stores,
    "customers": generate_customers,
    "products": generate_products,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, default=Path("configs/generation.yaml"))
    parser.add_argument("--output", type=Path, default=Path("data/landing"))
    parser.add_argument("--batch-id", type=validate_batch_id, default="B000000")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = _parse_args()
    settings = GenerationSettings.from_yaml(args.settings)

    for entity, generator in GENERATORS.items():
        frame = generator(settings)
        info = write_csv(frame, landing_path(args.output, entity, "snapshot", args.batch_id))
        logger.info(
            "%-10s rows=%-6d bytes=%-8d sha256=%s  %s",
            entity,
            info.record_count,
            info.size_bytes,
            info.sha256[:12],
            info.path,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
