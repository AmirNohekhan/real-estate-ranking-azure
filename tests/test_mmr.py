import pandas as pd

from real_estate_ranking.reranking.mmr import diversify


def test_diversify_empty_frame_returns_empty():
    frame = pd.DataFrame(columns=["ranking_score", "property_type", "asking_price"])
    assert diversify(frame, top_k=5).empty


def test_diversify_single_row_frame_returns_that_row():
    frame = pd.DataFrame(
        {"ranking_score": [1.0], "property_type": ["condo"], "asking_price": [200000]}
    )
    result = diversify(frame, top_k=3)
    assert len(result) == 1


def test_diversify_respects_top_k_and_returns_known_rows():
    frame = pd.DataFrame(
        {
            "ranking_score": [0.9, 0.8, 0.7, 0.6],
            "property_type": ["single_family", "single_family", "condo", "condo"],
            "asking_price": [300000, 310000, 150000, 900000],
        }
    )
    result = diversify(frame, top_k=2)
    assert len(result) == 2
    assert set(result.index).issubset(set(frame.index))
