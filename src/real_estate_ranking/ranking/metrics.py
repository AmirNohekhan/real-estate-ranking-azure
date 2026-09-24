import numpy as np


def ndcg_at_k(y: list[float] | np.ndarray, k: int = 10) -> float:
    """Normalized discounted cumulative gain of relevance labels `y`, truncated to the top `k`."""
    if k <= 0:
        raise ValueError("k must be positive")
    rel = np.asarray(y)[:k]
    dcg = np.sum((2**rel - 1) / np.log2(np.arange(len(rel)) + 2))
    ideal = np.sort(np.asarray(y))[::-1][:k]
    idcg = np.sum((2**ideal - 1) / np.log2(np.arange(len(ideal)) + 2))
    return float(dcg / idcg) if idcg else 0.0


def reciprocal_rank(y: list[float] | np.ndarray) -> float:
    """Inverse of the 1-indexed rank of the first relevant (label > 0) item in `y`, or 0 if none."""
    relevant = np.flatnonzero(np.asarray(y) > 0)
    return float(1 / (relevant[0] + 1)) if len(relevant) else 0.0
