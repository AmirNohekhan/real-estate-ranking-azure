from __future__ import annotations

import numpy as np
import pandas as pd

EARTH_RADIUS_MILES = 3958.7613


def haversine_miles(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    lat1, lon1 = np.radians(lat), np.radians(lon)
    lat2, lon2 = np.radians(lats), np.radians(lons)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def hard_filter(frame: pd.DataFrame, query: object) -> pd.DataFrame:
    distances = haversine_miles(
        query.latitude, query.longitude, frame.latitude.to_numpy(), frame.longitude.to_numpy()
    )
    mask = (
        (distances <= query.radius_miles)
        & frame.asking_price.between(query.min_price, query.max_price)
        & (frame.bedrooms >= query.min_bedrooms)
        & (frame.bathrooms >= query.min_bathrooms)
        & (frame.listing_status == "active")
    )
    if query.property_types:
        mask &= frame.property_type.isin(query.property_types)
    out = frame.loc[mask].copy()
    out["distance_miles"] = distances[mask]
    return out

