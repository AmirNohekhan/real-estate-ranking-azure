import numpy as np
import pytest

from real_estate_ranking.ranking.metrics import ndcg_at_k, reciprocal_rank
from real_estate_ranking.search.geo import haversine_miles


def test_ndcg_perfect_ordering_is_one_and_no_relevance_is_zero():
    assert ndcg_at_k([3, 2, 1, 0], 4) == pytest.approx(1.0)
    assert ndcg_at_k([0, 0, 0], 3) == 0.0


def test_ndcg_truncates_at_k():
    assert ndcg_at_k([0, 0, 3], 2) == 0.0


def test_reciprocal_rank_uses_first_relevant_position():
    assert reciprocal_rank([0, 0, 1, 1]) == pytest.approx(1 / 3)
    assert reciprocal_rank([0, 0]) == 0.0


def test_haversine_zero_distance_and_known_span():
    assert haversine_miles(39.0, -77.0, np.array([39.0]), np.array([-77.0]))[0] == pytest.approx(0.0)
    one_degree_lat = haversine_miles(39.0, -77.0, np.array([40.0]), np.array([-77.0]))[0]
    assert one_degree_lat == pytest.approx(69.09, abs=0.1)
