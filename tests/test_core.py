from pathlib import Path

from real_estate_ranking.data.pipeline import (
    generate_properties,
    simulate_listings,
    validate_properties,
)
from real_estate_ranking.events.publishers import LocalEventPublisher
from real_estate_ranking.experimentation.core import assign_variant, sample_ratio_mismatch
from real_estate_ranking.ranking.metrics import ndcg_at_k
from real_estate_ranking.retrieval.candidates import recall_at_k
from real_estate_ranking.schemas import InteractionEvent, SearchCriteria, SearchRequest
from real_estate_ranking.search.geo import hard_filter
from real_estate_ranking.serving.engine import SearchEngine
from real_estate_ranking.simulation.behavior import (
    generate_users,
    simulate_interactions,
    temporal_split,
)


def fixture_data():
    props, report = validate_properties(generate_properties(600)); return simulate_listings(props), report


def test_quality_and_unique_ids():
    listings, report = fixture_data()
    assert report.records_retained + report.records_rejected == 600
    assert report.records_retained == len(listings) and listings.property_id.is_unique


def test_hard_constraints_never_relaxed():
    listings, _ = fixture_data()
    q = SearchCriteria(latitude=39.084, longitude=-77.1528, radius_miles=15, min_price=500000,
                       max_price=800000, min_bedrooms=3, property_types=["townhouse"])
    result = hard_filter(listings, q)
    assert result.asking_price.between(500000, 800000).all()
    assert (result.bedrooms >= 3).all() and (result.property_type == "townhouse").all()
    assert (result.distance_miles <= 15).all()


def test_temporal_split_has_no_future_leakage():
    listings, _ = fixture_data(); events = simulate_interactions(generate_users(10), listings, 3)
    train, valid, test = temporal_split(events)
    assert train.timestamp.max() <= valid.timestamp.min() <= test.timestamp.min()


def test_metrics_and_retrieval():
    assert ndcg_at_k([3, 2, 0], 3) > ndcg_at_k([0, 2, 3], 3)
    assert recall_at_k(["a", "b", "c"], {"a", "c"}, 2) == .5


def test_assignment_stable_and_srm():
    assert assign_variant("user_1") == assign_variant("user_1")
    assert sample_ratio_mismatch(900, 100)


def test_event_idempotency(tmp_path: Path):
    publisher = LocalEventPublisher(tmp_path / "events.jsonl")
    event = InteractionEvent(user_id="u", property_id="p", listing_id="l", search_id="s",
        session_id="ss", event_type="click", position=1, exposure_propensity=1)
    assert publisher.publish(event) and not publisher.publish(event)


def test_end_to_end_personalization_and_contract():
    listings, _ = fixture_data(); users = generate_users(5); engine = SearchEngine(listings, users)
    req = SearchRequest.model_validate({"user_id":"user_000001","search":{"latitude":39.084,
        "longitude":-77.1528,"radius_miles":20,"min_price":300000,"max_price":1000000,
        "min_bedrooms":2,"property_types":["single_family","townhouse"]},"top_k":10})
    response = engine.search(req)
    assert response.results and [x.rank for x in response.results] == list(range(1, len(response.results)+1))
    assert all(300000 <= x.asking_price <= 1000000 for x in response.results)
    assert response.timings_ms["total"] > 0
