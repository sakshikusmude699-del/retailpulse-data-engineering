"""Per-entity deterministic random sources."""

from __future__ import annotations

import zlib
from dataclasses import dataclass

import numpy as np
from faker import Faker


@dataclass(frozen=True)
class GenerationContext:
    """Random generators for one entity.

    Each entity derives its own streams from (seed, entity name), so changing the
    size of one entity never changes the data generated for another.
    """

    rng: np.random.Generator
    faker: Faker

    @classmethod
    def for_entity(cls, seed: int, entity: str) -> GenerationContext:
        entity_seed = zlib.crc32(entity.encode("utf-8"))
        rng = np.random.default_rng([seed, entity_seed])
        faker = Faker("en_IN")
        faker.seed_instance((seed * 1_000_003 + entity_seed) % (2**32))
        return cls(rng=rng, faker=faker)
