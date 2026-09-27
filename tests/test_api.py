from fastapi.testclient import TestClient

from real_estate_ranking.serving.api import app, engine


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


def test_tour_rejects_empty_user_id():
    client = TestClient(app)
    property_id = str(engine.listings.property_id.iloc[0])
    response = client.post(f"/v1/properties/{property_id}/tour", params={"user_id": ""})
    assert response.status_code == 422


def test_internal_errors_do_not_leak_details(monkeypatch):
    def fail(_request):
        raise RuntimeError("secret connection string")

    monkeypatch.setattr("real_estate_ranking.serving.api.engine.search", fail)
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/v1/search", json={"user_id": "u", "search": {
        "latitude": 39.084, "longitude": -77.1528, "radius_miles": 20,
        "min_price": 300000, "max_price": 1000000}})
    assert response.status_code == 500
    assert response.json()["error"] == {
        "code": "INTERNAL_ERROR", "message": "An internal error occurred"
    }
    assert "secret" not in response.text
