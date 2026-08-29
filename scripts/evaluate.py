import json
from pathlib import Path

import numpy as np

from real_estate_ranking.ranking.metrics import ndcg_at_k, reciprocal_rank

# Deterministic smoke evaluation; full evaluation consumes persisted held-out event scores in production.
ranked = np.array([4, 2, 1, 0, 0]); baseline = np.array([0, 1, 4, 0, 2])
metrics = {"illustrative_smoke": True, "ranker_ndcg@10": ndcg_at_k(ranked, 10),
           "baseline_ndcg@10": ndcg_at_k(baseline, 10), "ranker_mrr": reciprocal_rank(ranked)}
Path("reports").mkdir(exist_ok=True); Path("reports/evaluation.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))

