from __future__ import annotations

import numpy as np
import pandas as pd


def diversify(frame: pd.DataFrame, top_k: int, relevance_weight: float = 0.82) -> pd.DataFrame:
    if frame.empty:
        return frame
    pool, selected = frame.copy(), []
    scores = pool.ranking_score.to_numpy(float)
    norm = (scores - scores.min()) / (np.ptp(scores) + 1e-9)
    while len(selected) < min(top_k, len(pool)):
        best, best_value = None, -np.inf
        for pos, (idx, row) in enumerate(pool.iterrows()):
            if idx in selected:
                continue
            similarity = 0.0
            for prior in selected:
                other = pool.loc[prior]
                similarity = max(similarity, 0.5 * (row.property_type == other.property_type) + 0.5 * np.exp(-abs(row.asking_price - other.asking_price) / 100_000))
            value = relevance_weight * norm[pos] - (1 - relevance_weight) * similarity
            if value > best_value:
                best, best_value = idx, value
        selected.append(best)
    return pool.loc[selected].copy()

