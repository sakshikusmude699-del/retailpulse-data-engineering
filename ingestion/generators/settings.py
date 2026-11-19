"""Typed generation settings loaded from YAML."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

REQUIRED_SIZES = (
    "stores",
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "inventory",
    "returns",
)


def _as_date(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


@dataclass(frozen=True)
class GenerationSettings:
    """Parameters that fully determine the generated dataset."""

    seed: int
    history_start: date
    history_end: date
    customer_registration_start: date
    sizes: dict[str, int]

    def __post_init__(self) -> None:
        missing = [name for name in REQUIRED_SIZES if name not in self.sizes]
        if missing:
            raise ValueError(f"Missing sizes in settings: {missing}")
        invalid = [name for name, value in self.sizes.items() if int(value) <= 0]
        if invalid:
            raise ValueError(f"Sizes must be positive integers: {invalid}")
        if not self.customer_registration_start < self.history_start < self.history_end:
            raise ValueError(
                "Dates must satisfy: customer_registration_start < history_start < history_end"
            )

    @classmethod
    def from_yaml(cls, path: Path | str) -> GenerationSettings:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(
            seed=int(raw["seed"]),
            history_start=_as_date(raw["history_start"]),
            history_end=_as_date(raw["history_end"]),
            customer_registration_start=_as_date(raw["customer_registration_start"]),
            sizes={name: int(value) for name, value in raw["sizes"].items()},
        )
