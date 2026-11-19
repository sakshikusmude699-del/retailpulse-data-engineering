"""Static reference data that gives the generated dataset realistic structure.

All names and brands are fictional. Prices are in INR.
"""

from __future__ import annotations

from dataclasses import dataclass

# (city, state, region, relative population weight)
LOCATIONS: tuple[tuple[str, str, str, int], ...] = (
    ("Mumbai", "Maharashtra", "West", 20),
    ("New Delhi", "Delhi", "North", 18),
    ("Bengaluru", "Karnataka", "South", 16),
    ("Hyderabad", "Telangana", "South", 12),
    ("Chennai", "Tamil Nadu", "South", 11),
    ("Kolkata", "West Bengal", "East", 11),
    ("Pune", "Maharashtra", "West", 9),
    ("Ahmedabad", "Gujarat", "West", 8),
    ("Jaipur", "Rajasthan", "North", 5),
    ("Lucknow", "Uttar Pradesh", "North", 5),
    ("Noida", "Uttar Pradesh", "North", 5),
    ("Surat", "Gujarat", "West", 5),
    ("Kochi", "Kerala", "South", 4),
    ("Nagpur", "Maharashtra", "West", 4),
    ("Coimbatore", "Tamil Nadu", "South", 3),
    ("Mysuru", "Karnataka", "South", 3),
    ("Chandigarh", "Chandigarh", "North", 3),
    ("Patna", "Bihar", "East", 3),
    ("Bhubaneswar", "Odisha", "East", 3),
    ("Guwahati", "Assam", "East", 2),
)

STORE_TYPES: tuple[str, ...] = ("Standard", "Express", "Outlet")
STORE_TYPE_PROBABILITIES: tuple[float, ...] = (0.60, 0.25, 0.15)
FLAGSHIP_STORE_COUNT = 5
STORE_AREA_SUFFIXES: tuple[str, ...] = ("Central", "Mall Road", "Riverside", "Old Town")

CUSTOMER_SEGMENTS: tuple[str, ...] = ("Premium", "Regular", "Budget")
CUSTOMER_SEGMENT_PROBABILITIES: tuple[float, ...] = (0.12, 0.58, 0.30)


@dataclass(frozen=True)
class SubcategorySpec:
    """Brands, price band (INR) and margin band for one product subcategory."""

    brands: tuple[str, ...]
    price_min: int
    price_max: int
    margin_min: float
    margin_max: float


PRODUCT_CATALOG: dict[str, dict[str, SubcategorySpec]] = {
    "Electronics": {
        "Mobiles": SubcategorySpec(
            ("VoltEdge", "NovaTech", "PulseOne", "Zenix"), 8_000, 60_000, 0.08, 0.15
        ),
        "Laptops": SubcategorySpec(
            ("VoltEdge", "NovaTech", "Zenix", "ByteWorks"), 30_000, 120_000, 0.06, 0.12
        ),
        "Audio": SubcategorySpec(("PulseOne", "SoundArc", "NovaTech"), 800, 15_000, 0.25, 0.40),
    },
    "Fashion": {
        "Menswear": SubcategorySpec(("UrbanLoom", "Threadline", "Kestrel"), 500, 4_000, 0.35, 0.55),
        "Womenswear": SubcategorySpec(
            ("UrbanLoom", "Silkroute", "Threadline"), 600, 6_000, 0.35, 0.55
        ),
        "Footwear": SubcategorySpec(("StrideCo", "Kestrel", "UrbanLoom"), 800, 7_000, 0.30, 0.50),
    },
    "Home & Kitchen": {
        "Cookware": SubcategorySpec(
            ("HearthCraft", "Panhandle", "Kestrel"), 400, 6_000, 0.30, 0.45
        ),
        "Furniture": SubcategorySpec(
            ("WoodNest", "HearthCraft", "Casalux"), 3_000, 45_000, 0.20, 0.35
        ),
        "Home Decor": SubcategorySpec(("Casalux", "WoodNest", "Silkroute"), 300, 8_000, 0.35, 0.55),
    },
    "Grocery": {
        "Staples": SubcategorySpec(
            ("FarmFresh", "GoldenHarvest", "DailyBasket"), 40, 900, 0.08, 0.18
        ),
        "Snacks": SubcategorySpec(("CrunchCo", "DailyBasket", "FarmFresh"), 20, 500, 0.15, 0.30),
        "Beverages": SubcategorySpec(
            ("DailyBasket", "CrunchCo", "GoldenHarvest"), 30, 800, 0.15, 0.30
        ),
    },
    "Beauty": {
        "Skincare": SubcategorySpec(("GlowLab", "PureRoot", "Silkroute"), 200, 3_500, 0.40, 0.60),
        "Haircare": SubcategorySpec(("PureRoot", "GlowLab", "Kestrel"), 150, 2_500, 0.35, 0.55),
    },
    "Sports": {
        "Fitness": SubcategorySpec(("StrideCo", "IronPeak", "Kestrel"), 500, 25_000, 0.25, 0.40),
        "Outdoor": SubcategorySpec(("IronPeak", "TrailForge", "StrideCo"), 800, 20_000, 0.25, 0.40),
    },
}

# Share of the product range per category (sums to 1.0)
CATEGORY_WEIGHTS: dict[str, float] = {
    "Electronics": 0.18,
    "Fashion": 0.26,
    "Home & Kitchen": 0.18,
    "Grocery": 0.18,
    "Beauty": 0.10,
    "Sports": 0.10,
}

PRODUCT_SERIES: tuple[str, ...] = ("Lite", "Classic", "Plus", "Pro", "Max")
