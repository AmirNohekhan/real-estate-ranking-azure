from __future__ import annotations

from time import perf_counter
from uuid import uuid4

import pandas as pd

from real_estate_ranking.experimentation.core import assign_variant
from real_estate_ranking.ranking.model import PairwiseRanker, build_features
from real_estate_ranking.reranking.mmr import diversify
from real_estate_ranking.retrieval.candidates import CandidateRetriever
from real_estate_ranking.schemas import SearchRequest, SearchResponse, SearchResult
from real_estate_ranking.search.geo import hard_filter


def reason_codes(row: pd.Series, user: pd.Series) -> list[str]:
    reasons = ["MATCHES_PRICE_RANGE"]
    if row.property_type == user.preferred_type:
        reasons.append("PREFERRED_PROPERTY_TYPE")
    if abs(row.bedrooms - user.preferred_bedrooms) <= 1:
        reasons.append("MATCHES_BEDROOM_PREFERENCE")
    if abs(row.square_feet - user.preferred_sqft) < 600:
        reasons.append("MATCHES_SIZE_PREFERENCE")
    if row.distance_miles < 5:
        reasons.append("CLOSE_TO_SEARCH_AREA")
    return reasons[:3]


class SearchEngine:
    def __init__(self, listings: pd.DataFrame, users: pd.DataFrame, events: pd.DataFrame | None = None,
                 ranker: PairwiseRanker | None = None):
        self.listings, self.users = listings, users.set_index("user_id", drop=False)
        self.retriever = CandidateRetriever(listings, events)
        self.ranker = ranker or PairwiseRanker()

    def search(self, request: SearchRequest) -> SearchResponse:
        timings, started = {}, perf_counter()
        eligible = hard_filter(self.listings, request.search)
        timings["filter"] = (perf_counter() - started) * 1000
        user = self.users.loc[request.user_id] if request.user_id in self.users.index else pd.Series(
            {"preferred_price": (request.search.min_price + request.search.max_price)/2,
             "preferred_sqft": 2000, "preferred_bedrooms": request.search.min_bedrooms,
             "preferred_type": request.search.property_types[0] if request.search.property_types else "single_family",
             "garage_affinity": 0.5})
        mark = perf_counter(); candidates = self.retriever.retrieve(eligible, user); timings["retrieval"] = (perf_counter()-mark)*1000
        mark = perf_counter(); features = build_features(candidates, user, self.retriever.popularity); timings["features"] = (perf_counter()-mark)*1000
        mark = perf_counter(); candidates["ranking_score"] = self.ranker.score(features); candidates = candidates.sort_values("ranking_score", ascending=False); timings["ranking"] = (perf_counter()-mark)*1000
        mark = perf_counter(); final = diversify(candidates.head(max(request.top_k*3, 50)), request.top_k); timings["reranking"] = (perf_counter()-mark)*1000
        results = [SearchResult(property_id=r.property_id, listing_id=r.listing_id, rank=i,
                    score=round(float(r.ranking_score), 6), distance_miles=round(float(r.distance_miles), 3),
                    asking_price=float(r.asking_price), property_type=r.property_type, bedrooms=int(r.bedrooms),
                    reasons=reason_codes(r, user)) for i, (_, r) in enumerate(final.iterrows(), 1)]
        timings["total"] = (perf_counter()-started)*1000
        return SearchResponse(request_id=str(uuid4()), model_version="pairwise-ltr-0.1",
            experiment_variant=assign_variant(request.user_id), results=results,
            timings_ms={k: round(v, 3) for k, v in timings.items()})

