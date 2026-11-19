from datetime import date

import pandas as pd
import pytest

from ingestion.generators.settings import GenerationSettings
from ingestion.utils.files import landing_path, sha256_of_file, validate_batch_id, write_csv

VALID_SIZES = {
    name: 10
    for name in (
        "stores",
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
        "inventory",
        "returns",
    )
}


def test_write_csv_counts_records_and_uses_lf(tmp_path):
    frame = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
    info = write_csv(frame, tmp_path / "out" / "sample.csv")
    assert info.record_count == 3
    assert info.size_bytes == info.path.stat().st_size
    assert b"\r" not in info.path.read_bytes()


def test_identical_data_gives_identical_checksum(tmp_path):
    frame = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    first = write_csv(frame, tmp_path / "one.csv")
    second = write_csv(frame, tmp_path / "two.csv")
    assert first.sha256 == second.sha256 == sha256_of_file(first.path)


def test_batch_id_validation():
    assert validate_batch_id("B000012") == "B000012"
    for bad in ("000012", "B12", "b000012", "B0000123"):
        with pytest.raises(ValueError):
            validate_batch_id(bad)


def test_landing_path_layout(tmp_path):
    path = landing_path(tmp_path, "customers", "snapshot", "B000000")
    assert path == tmp_path / "customers" / "snapshot" / "customers_B000000.csv"


def test_settings_reject_bad_dates():
    with pytest.raises(ValueError, match="Dates must satisfy"):
        GenerationSettings(
            seed=1,
            history_start=date(2025, 1, 1),
            history_end=date(2024, 1, 1),
            customer_registration_start=date(2023, 1, 1),
            sizes=VALID_SIZES,
        )


def test_settings_reject_missing_sizes():
    with pytest.raises(ValueError, match="Missing sizes"):
        GenerationSettings(
            seed=1,
            history_start=date(2025, 1, 1),
            history_end=date(2026, 1, 1),
            customer_registration_start=date(2023, 1, 1),
            sizes={"stores": 5},
        )


def test_settings_load_from_yaml(tmp_path):
    path = tmp_path / "gen.yaml"
    sizes = "\n".join(f"  {name}: 5" for name in VALID_SIZES)
    path.write_text(
        'seed: 3\nhistory_start: "2025-01-01"\nhistory_end: "2026-10-31"\n'
        f'customer_registration_start: "2023-01-01"\nsizes:\n{sizes}\n',
        encoding="utf-8",
    )
    settings = GenerationSettings.from_yaml(path)
    assert settings.seed == 3
    assert settings.history_end == date(2026, 10, 31)
