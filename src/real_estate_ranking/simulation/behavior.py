from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd


def generate_users(n: int = 120, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "user_id": [f"user_{i:06d}" for i in range(n)],
            "preferred_price": rng.normal(650_000, 180_000, n).clip(250_000, 1_300_000),
            "preferred_sqft": rng.normal(2200, 650, n).clip(700, 5000),
            "preferred_bedrooms": rng.integers(2, 6, n),
            "preferred_type": rng.choice(["single_family", "townhouse", "condo"], n, p=[0.55, 0.3, 0.15]),
            "preferred_latitude": rng.normal(39.0840, 0.07, n),
            "preferred_longitude": rng.normal(-77.1528, 0.08, n),
            "garage_affinity": rng.uniform(0, 1, n),
            "intent": rng.beta(2, 4, n),
        }
    )


def compatibility(user: pd.Series, props: pd.DataFrame) -> np.ndarray:
    price = np.exp(-np.abs(props.asking_price - user.preferred_price) / 250_000)
    size = np.exp(-np.abs(props.square_feet - user.preferred_sqft) / 1100)
    beds = np.exp(-np.abs(props.bedrooms - user.preferred_bedrooms) / 2)
    ptype = (props.property_type == user.preferred_type).astype(float).to_numpy()
    garage = np.minimum(props.garage_spaces.to_numpy(), 1) * user.garage_affinity
    return 0.28 * price + 0.22 * size + 0.15 * beds + 0.23 * ptype + 0.12 * garage


def simulate_interactions(
    users: pd.DataFrame, listings: pd.DataFrame, sessions_per_user: int = 6, seed: int = 11
) -> pd.DataFrame:
    """Chronological biased impression funnel; labels are generated from compatibility."""
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for ui, user in users.iterrows():
        utility = compatibility(user, listings) + rng.normal(0, 0.08, len(listings))
        for session in range(sessions_per_user):
            # preference evolution: price ceiling drifts modestly over time
            evolved = utility - np.abs(listings.asking_price - user.preferred_price * (1 + session * 0.008)) / 3_000_000
            shown = np.argpartition(evolved, -25)[-25:]
            shown = shown[np.argsort(evolved[shown])[::-1]]
            ts = start + timedelta(days=int(ui * sessions_per_user + session))
            for pos, idx in enumerate(shown, 1):
                propensity = 1 / np.log2(pos + 1)
                u = float(evolved[idx])
                click = rng.random() < (0.03 + 0.30 * u * propensity)
                save = click and rng.random() < (0.03 + 0.20 * u * user.intent)
                tour = save and rng.random() < (0.015 + 0.10 * user.intent)
                contact = (tour or save) and rng.random() < (0.01 + 0.05 * user.intent)
                label = 4 if contact else 3 if tour else 2 if save else 1 if click else 0
                rows.append(
                    {
                        "user_id": user.user_id,
                        "property_id": listings.iloc[idx].property_id,
                        "search_id": f"search_{ui:04d}_{session:03d}",
                        "session_id": f"session_{ui:04d}_{session:03d}",
                        "timestamp": ts + timedelta(seconds=pos),
                        "position": pos,
                        "exposure_propensity": propensity,
                        "relevance": label,
                    }
                )
    return pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)


def temporal_split(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = events.sort_values("timestamp")
    a, b = int(len(ordered) * 0.70), int(len(ordered) * 0.85)
    return ordered.iloc[:a].copy(), ordered.iloc[a:b].copy(), ordered.iloc[b:].copy()

