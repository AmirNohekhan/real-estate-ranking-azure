from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PROPERTY_TYPES = np.array(["single_family", "townhouse", "condo"])


@dataclass(frozen=True)
class QualityReport:
    records_downloaded: int
    records_rejected: int
    records_transformed: int
    records_retained: int


def stable_property_id(source_id: str) -> str:
    return "prop_" + hashlib.sha256(f"md-sdat:{source_id}".encode()).hexdigest()[:16]


def generate_properties(n: int = 2500, seed: int = 42) -> pd.DataFrame:
    """Offline fallback centered on Rockville; every physical field is marked simulated."""
    rng = np.random.default_rng(seed)
    ptype = rng.choice(PROPERTY_TYPES, n, p=[0.58, 0.27, 0.15])
    bedrooms = np.where(ptype == "condo", rng.integers(1, 4, n), rng.integers(2, 6, n))
    sqft = np.maximum(550, bedrooms * rng.normal(520, 100, n)).round().astype(int)
    assessed = (110_000 + sqft * rng.normal(245, 35, n)).clip(150_000, 1_800_000).round()
    source_ids = [f"synthetic_{i:07d}" for i in range(n)]
    frame = pd.DataFrame(
        {
            "property_id": [stable_property_id(x) for x in source_ids],
            "source_record_id": source_ids,
            "latitude": rng.normal(39.0840, 0.105, n),
            "longitude": rng.normal(-77.1528, 0.135, n),
            "county": "Montgomery",
            "city": rng.choice(["Rockville", "Gaithersburg", "Bethesda", "Silver Spring"], n),
            "state": "MD",
            "zip_code": rng.choice([20850, 20852, 20878, 20814, 20910], n).astype(str),
            "property_type": ptype,
            "assessed_value": assessed,
            "bedrooms": bedrooms,
            "bathrooms": np.maximum(1, bedrooms - rng.integers(0, 2, n) + rng.choice([0, 0.5], n)),
            "square_feet": sqft,
            "lot_size": np.where(ptype == "single_family", rng.lognormal(8.8, 0.55, n), rng.lognormal(7, 0.4, n)).round(),
            "year_built": rng.integers(1940, 2025, n),
            "garage_spaces": rng.choice([0, 1, 2, 3], n, p=[0.25, 0.3, 0.4, 0.05]),
            "data_source": "SYNTHETIC_FALLBACK",
            "source_updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return frame


def simulate_listings(properties: pd.DataFrame, seed: int = 43) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = properties.copy()
    variation = rng.lognormal(0.08, 0.12, len(out))
    out["listing_id"] = "list_" + out["property_id"].str.removeprefix("prop_")
    out["asking_price"] = (out["assessed_value"] * variation).round(-3)
    out["listing_status"] = rng.choice(["active", "pending"], len(out), p=[0.92, 0.08])
    out["days_on_market"] = rng.gamma(2.2, 14, len(out)).round().astype(int)
    out["price_change_percent"] = rng.normal(-0.01, 0.025, len(out)).clip(-0.15, 0.1)
    out["listing_freshness"] = np.exp(-out["days_on_market"] / 45)
    out["listing_provenance"] = "SIMULATED"
    return out


def validate_properties(frame: pd.DataFrame) -> tuple[pd.DataFrame, QualityReport]:
    required = {"property_id", "latitude", "longitude", "square_feet", "year_built"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    valid = (
        frame["property_id"].notna()
        & ~frame["property_id"].duplicated()
        & frame["latitude"].between(38.7, 39.4)
        & frame["longitude"].between(-77.6, -76.8)
        & frame["square_feet"].between(200, 20_000)
        & frame["year_built"].between(1700, datetime.now().year + 2)
    )
    clean = frame.loc[valid].reset_index(drop=True)
    return clean, QualityReport(len(frame), int((~valid).sum()), len(frame), len(clean))


def write_inventory(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)

