from fastapi.testclient import TestClient

from real_estate_ranking.serving.api import app


def test_health_and_search_api():
    client = TestClient(app); assert client.get("/health").json() == {"status":"ok"}
    response = client.post("/v1/search", json={"user_id":"user_000001","search":{"latitude":39.084,
        "longitude":-77.1528,"radius_miles":20,"min_price":300000,"max_price":1000000,
        "min_bedrooms":2,"property_types":["single_family","townhouse"]},"top_k":5})
    assert response.status_code == 200 and len(response.json()["results"]) <= 5


def test_event_api_rejects_unknown_event_types():
    response = TestClient(app).post("/v1/events", json={
        "user_id": "u", "property_id": "p", "listing_id": "l", "search_id": "s",
        "session_id": "ss", "event_type": "opened_email", "position": 1,
        "exposure_propensity": 1,
    })
    assert response.status_code == 422
