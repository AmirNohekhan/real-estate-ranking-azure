from pathlib import Path

import numpy as np
import pandas as pd

from real_estate_ranking.ranking.model import PairwiseRanker, build_features

listings = pd.read_parquet("data/processed/listings.parquet").set_index("property_id", drop=False)
users = pd.read_parquet("data/processed/users.parquet").set_index("user_id", drop=False)
events = pd.read_parquet("data/processed/events.parquet").sort_values("timestamp")
events = events.iloc[: int(len(events) * .7)]
rows, labels, groups, propensities = [], [], [], []
for search_id, group in events.groupby("search_id"):
    user = users.loc[group.user_id.iloc[0]]; candidates = listings.loc[group.property_id].copy()
    candidates["retrieval_score"] = .5; candidates["distance_miles"] = 0.0
    rows.append(build_features(candidates, user)); labels.extend(group.relevance); groups.extend([search_id]*len(group)); propensities.extend(group.exposure_propensity)
ranker = PairwiseRanker().fit(pd.concat(rows), np.asarray(labels), np.asarray(groups), np.asarray(propensities))
ranker.save(Path("models/ranker.pkl")); print(f"trained pairwise ranker on {len(labels)} impressions")

