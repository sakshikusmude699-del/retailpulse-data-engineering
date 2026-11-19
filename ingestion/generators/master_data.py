"""Generators for master (reference) entities: stores, customers and products."""

from __future__ import annotations

import re
from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd

from ingestion.generators.context import GenerationContext
from ingestion.generators.reference_data import (
    CATEGORY_WEIGHTS,
    CUSTOMER_SEGMENT_PROBABILITIES,
    CUSTOMER_SEGMENTS,
    FLAGSHIP_STORE_COUNT,
    LOCATIONS,
    PRODUCT_CATALOG,
    PRODUCT_SERIES,
    STORE_AREA_SUFFIXES,
    STORE_TYPE_PROBABILITIES,
    STORE_TYPES,
)
from ingestion.generators.settings import GenerationSettings

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _price_point(raw_price: float) -> float:
    """Retail-style price ending in 9, e.g. 1234.5 -> 1229."""
    return float(max(int(round(raw_price / 10.0)) * 10 - 1, 9))


def generate_stores(settings: GenerationSettings) -> pd.DataFrame:
    """One row per store; the largest cities get extra stores after one per city."""
    ctx = GenerationContext.for_entity(settings.seed, "stores")
    ordered_locations = sorted(LOCATIONS, key=lambda loc: (-loc[3], loc[0]))
    updated_at = datetime.combine(settings.customer_registration_start, time.min)

    stores_per_city: dict[str, int] = {}
    rows = []
    for store_number in range(1, settings.sizes["stores"] + 1):
        city, state, region, _weight = ordered_locations[
            (store_number - 1) % len(ordered_locations)
        ]
        occurrence = stores_per_city.get(city, 0)
        stores_per_city[city] = occurrence + 1

        if store_number <= FLAGSHIP_STORE_COUNT:
            store_type = "Flagship"
        else:
            store_type = str(ctx.rng.choice(STORE_TYPES, p=STORE_TYPE_PROBABILITIES))

        suffix = STORE_AREA_SUFFIXES[occurrence % len(STORE_AREA_SUFFIXES)]
        rows.append(
            {
                "store_id": f"STORE-{store_number:03d}",
                "store_name": f"RetailPulse {city} {suffix}",
                "city": city,
                "state": state,
                "region": region,
                "store_type": store_type,
                "updated_at": updated_at.strftime(TIMESTAMP_FORMAT),
            }
        )
    return pd.DataFrame(rows)


def generate_customers(settings: GenerationSettings) -> pd.DataFrame:
    """Customers spread across cities by population, with growing sign-ups over time."""
    ctx = GenerationContext.for_entity(settings.seed, "customers")
    count = settings.sizes["customers"]

    weights = np.array([loc[3] for loc in LOCATIONS], dtype=float)
    city_indexes = ctx.rng.choice(len(LOCATIONS), size=count, p=weights / weights.sum())
    segment_indexes = ctx.rng.choice(
        len(CUSTOMER_SEGMENTS), size=count, p=CUSTOMER_SEGMENT_PROBABILITIES
    )

    span_days = (settings.history_end - settings.customer_registration_start).days
    # Beta(1.5, 1) skews registrations toward recent dates (a growing customer base).
    offsets = np.sort((span_days * ctx.rng.beta(1.5, 1.0, size=count)).astype(int))
    seconds = ctx.rng.integers(0, 86_400, size=count)

    rows = []
    for index in range(count):
        city, state, _region, _weight = LOCATIONS[int(city_indexes[index])]
        first_name = ctx.faker.first_name()
        last_name = ctx.faker.last_name()
        registered_on = settings.customer_registration_start + timedelta(days=int(offsets[index]))
        registered_at = datetime.combine(registered_on, time.min) + timedelta(
            seconds=int(seconds[index])
        )
        customer_number = index + 1
        rows.append(
            {
                "customer_id": f"CUST-{customer_number:06d}",
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{_slug(first_name)}.{_slug(last_name)}{customer_number}@example.com",
                "city": city,
                "state": state,
                "registration_date": registered_on.isoformat(),
                "customer_segment": CUSTOMER_SEGMENTS[int(segment_indexes[index])],
                "updated_at": registered_at.strftime(TIMESTAMP_FORMAT),
            }
        )
    return pd.DataFrame(rows)


def generate_products(settings: GenerationSettings) -> pd.DataFrame:
    """Products with category-specific price bands and margins."""
    ctx = GenerationContext.for_entity(settings.seed, "products")
    count = settings.sizes["products"]

    categories = list(CATEGORY_WEIGHTS)
    probabilities = np.array([CATEGORY_WEIGHTS[name] for name in categories], dtype=float)
    category_indexes = ctx.rng.choice(
        len(categories), size=count, p=probabilities / probabilities.sum()
    )

    rows = []
    for index in range(count):
        category = categories[int(category_indexes[index])]
        subcategories = list(PRODUCT_CATALOG[category])
        subcategory = subcategories[int(ctx.rng.integers(len(subcategories)))]
        spec = PRODUCT_CATALOG[category][subcategory]

        brand = spec.brands[int(ctx.rng.integers(len(spec.brands)))]
        series = PRODUCT_SERIES[int(ctx.rng.integers(len(PRODUCT_SERIES)))]
        model_number = int(ctx.rng.integers(100, 1000))

        # Beta(1.5, 3) skews toward the cheaper end of each band, as in real catalogs.
        raw_price = spec.price_min + (spec.price_max - spec.price_min) * float(
            ctx.rng.beta(1.5, 3.0)
        )
        unit_price = _price_point(raw_price)
        margin = float(ctx.rng.uniform(spec.margin_min, spec.margin_max))
        cost_price = round(unit_price * (1.0 - margin), 2)

        launched_on = settings.history_start - timedelta(days=int(ctx.rng.integers(30, 600)))
        rows.append(
            {
                "product_id": f"PROD-{index + 1:05d}",
                "product_name": f"{brand} {subcategory} {series} {model_number}",
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "unit_price": unit_price,
                "cost_price": cost_price,
                "updated_at": datetime.combine(launched_on, time.min).strftime(TIMESTAMP_FORMAT),
            }
        )
    return pd.DataFrame(rows)
