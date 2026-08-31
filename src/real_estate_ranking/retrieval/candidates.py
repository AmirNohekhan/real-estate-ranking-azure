from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from real_estate_ranking.simulation.behavior import compatibility

VECTOR_COLS = ["asking_price", "bedrooms", "bathrooms", "square_feet", "garage_spaces"]


class CandidateRetriever:
    """Blends popularity, preference similarity and vector retrieval with source attribution."""

    def __init__(self, listings: pd.DataFrame, events: pd.DataFrame | None = None):
        self.listings = listings
        self.scaler = StandardScaler().fit(listings[VECTOR_COLS])
        self.vectors = self.scaler.transform(listings[VECTOR_COLS])
        self.popularity = (
            events.groupby("property_id").relevance.sum() if events is not None else pd.Series(dtype=float)
        )

    def retrieve(self, eligible: pd.DataFrame, user: pd.Series, limit: int = 500) -> pd.DataFrame:
        if eligible.empty:
            return eligible.assign(retrieval_score=pd.Series(dtype=float), retrieval_source=pd.Series(dtype=str))
        content = compatibility(user, eligible)
        ids = eligible.property_id
        pop = ids.map(self.popularity).fillna(0).to_numpy(dtype=float)
        pop = np.log1p(pop) / max(np.log1p(pop).max(), 1)
        user_vector = pd.DataFrame(
            [[user.preferred_price, user.preferred_bedrooms, max(1, user.preferred_bedrooms - 1), user.preferred_sqft, user.garage_affinity * 2]],
            columns=VECTOR_COLS,
        )
        uv = self.scaler.transform(user_vector)[0]
        pv = self.scaler.transform(eligible[VECTOR_COLS])
        embedding = 1 / (1 + np.linalg.norm(pv - uv, axis=1))
        score = 0.42 * content + 0.23 * pop + 0.35 * embedding
        source = np.choose(np.argmax(np.c_[content, pop, embedding], axis=1), ["content", "popularity", "embedding"])
        out = eligible.assign(retrieval_score=score, retrieval_source=source)
        return out.nlargest(min(limit, len(out)), "retrieval_score")


def recall_at_k(candidates: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    return len(set(candidates[:k]) & relevant) / len(relevant) if relevant else 0.0
