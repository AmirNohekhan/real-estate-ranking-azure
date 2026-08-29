from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "retrieval_score", "distance_miles", "price_match", "size_match", "bedroom_match",
    "type_match", "freshness", "popularity", "embedding_similarity",
]


def build_features(candidates: pd.DataFrame, user: pd.Series, popularity: pd.Series | None = None) -> pd.DataFrame:
    out = pd.DataFrame(index=candidates.index)
    out["retrieval_score"] = candidates.get("retrieval_score", 0.0)
    out["distance_miles"] = candidates.get("distance_miles", 0.0)
    out["price_match"] = np.exp(-np.abs(candidates.asking_price - user.preferred_price) / 250_000)
    out["size_match"] = np.exp(-np.abs(candidates.square_feet - user.preferred_sqft) / 1100)
    out["bedroom_match"] = np.exp(-np.abs(candidates.bedrooms - user.preferred_bedrooms))
    out["type_match"] = (candidates.property_type == user.preferred_type).astype(float)
    out["freshness"] = candidates.listing_freshness
    out["popularity"] = candidates.property_id.map(popularity).fillna(0) if popularity is not None else 0.0
    out["embedding_similarity"] = out["price_match"] * 0.5 + out["size_match"] * 0.5
    return out[FEATURES]


class PairwiseRanker:
    """Query-group-aware pairwise learning-to-rank using inverse-propensity sample weights."""

    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=0.001, random_state=42)
        self.fitted = False

    def fit(self, x: pd.DataFrame, y: np.ndarray, groups: np.ndarray, propensity: np.ndarray) -> "PairwiseRanker":
        pairs, labels, weights = [], [], []
        for group in np.unique(groups):
            idx = np.flatnonzero(groups == group)
            for a in idx:
                for b in idx:
                    if y[a] > y[b]:
                        diff = x.iloc[a].to_numpy(float) - x.iloc[b].to_numpy(float)
                        pairs.extend([diff, -diff]); labels.extend([1, 0])
                        w = min(10.0, 1 / max(propensity[a], 0.05))
                        weights.extend([w, w])
        if not pairs:
            raise ValueError("training requires at least one unequal-relevance pair")
        px = self.scaler.fit_transform(np.asarray(pairs))
        self.model.fit(px, labels, sample_weight=weights)
        self.fitted = True
        return self

    def score(self, x: pd.DataFrame) -> np.ndarray:
        if not self.fitted:
            # documented cold/local bootstrap heuristic
            return (0.35*x.price_match + 0.25*x.type_match + 0.2*x.size_match + 0.15*x.retrieval_score + 0.05*x.freshness).to_numpy()
        return self.model.decision_function(self.scaler.transform(x[FEATURES]))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(self))

    @classmethod
    def load(cls, path: Path) -> "PairwiseRanker":
        return pickle.loads(path.read_bytes())

