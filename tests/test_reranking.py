import pandas as pd
import pytest

from real_estate_ranking.ranking.metrics import reciprocal_rank
from real_estate_ranking.reranking.mmr import diversify


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ranking_score": [0.90, 0.89, 0.88, 0.50],
            "property_type": ["house", "house", "house", "condo"],
            "asking_price": [500_000, 505_000, 510_000, 300_000],
        }
    )


def test_diversify_empty_frame_is_returned_unchanged():
    empty = _frame().iloc[0:0]
    assert diversify(empty, top_k=5).empty


def test_diversify_respects_top_k_and_returns_unique_rows():
    out = diversify(_frame(), top_k=3)
    assert len(out) == 3
    assert out.index.is_unique


def test_diversify_caps_at_pool_size():
    assert len(diversify(_frame(), top_k=10)) == 4


def test_diversify_keeps_best_first_and_promotes_dissimilar_listing():
    out = diversify(_frame(), top_k=2, relevance_weight=0.3)
    assert out.index[0] == 0
    assert out.iloc[1].property_type == "condo"


def test_diversify_pure_relevance_matches_score_order():
    out = diversify(_frame(), top_k=4, relevance_weight=1.0)
    assert list(out.index) == [0, 1, 2, 3]


def test_reciprocal_rank():
    assert reciprocal_rank([0, 0, 1, 1]) == pytest.approx(1 / 3)
    assert reciprocal_rank([1, 0]) == 1.0
    assert reciprocal_rank([0, 0]) == 0.0
