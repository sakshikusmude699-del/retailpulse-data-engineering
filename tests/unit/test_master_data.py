from dataclasses import replace
from datetime import date

import pandas as pd
import pytest

from ingestion.generators.master_data import (
    generate_customers,
    generate_products,
    generate_stores,
)
from ingestion.generators.reference_data import (
    CUSTOMER_SEGMENTS,
    LOCATIONS,
    PRODUCT_CATALOG,
)
from ingestion.generators.settings import GenerationSettings


@pytest.fixture
def settings() -> GenerationSettings:
    return GenerationSettings(
        seed=7,
        history_start=date(2025, 1, 1),
        history_end=date(2026, 10, 31),
        customer_registration_start=date(2023, 1, 1),
        sizes={
            "stores": 30,
            "customers": 400,
            "products": 120,
            "orders": 1000,
            "order_items": 2000,
            "payments": 1000,
            "inventory": 500,
            "returns": 50,
        },
    )


def test_store_count_and_unique_ids(settings):
    stores = generate_stores(settings)
    assert len(stores) == 30
    assert stores["store_id"].is_unique
    assert (stores["store_type"] == "Flagship").sum() == 5


def test_store_locations_are_consistent(settings):
    stores = generate_stores(settings)
    valid = {(city, state, region) for city, state, region, _ in LOCATIONS}
    actual = set(stores[["city", "state", "region"]].itertuples(index=False, name=None))
    assert actual <= valid


def test_customers_are_valid(settings):
    customers = generate_customers(settings)
    assert len(customers) == 400
    assert customers["customer_id"].is_unique
    assert customers["email"].is_unique
    assert set(customers["customer_segment"]) <= set(CUSTOMER_SEGMENTS)
    registered = pd.to_datetime(customers["registration_date"])
    assert registered.min() >= pd.Timestamp(settings.customer_registration_start)
    assert registered.max() <= pd.Timestamp(settings.history_end)
    assert registered.is_monotonic_increasing


def test_products_are_valid(settings):
    products = generate_products(settings)
    assert len(products) == 120
    assert products["product_id"].is_unique
    assert (products["cost_price"] > 0).all()
    assert (products["unit_price"] > products["cost_price"]).all()
    for row in products.itertuples():
        spec = PRODUCT_CATALOG[row.category][row.subcategory]
        assert row.brand in spec.brands


def test_generation_is_deterministic(settings):
    pd.testing.assert_frame_equal(generate_customers(settings), generate_customers(settings))
    pd.testing.assert_frame_equal(generate_products(settings), generate_products(settings))


def test_entities_are_independent(settings):
    bigger = replace(settings, sizes={**settings.sizes, "customers": 900})
    pd.testing.assert_frame_equal(generate_products(settings), generate_products(bigger))


def test_different_seed_changes_output(settings):
    other = replace(settings, seed=8)
    assert not generate_customers(settings).equals(generate_customers(other))
