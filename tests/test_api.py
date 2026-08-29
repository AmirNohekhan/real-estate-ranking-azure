from fastapi.testclient import TestClient

from real_estate_ranking.serving.api import app


def test_health_and_search_api():
    client = TestClient(app); assert client.get("/health").json() == {"status":"ok"}
    response = client.post("/v1/search", json={"user_id":"user_000001","search":{"latitude":39.084,
        "longitude":-77.1528,"radius_miles":20,"min_price":300000,"max_price":1000000,
        "min_bedrooms":2,"property_types":["single_family","townhouse"]},"top_k":5})
    assert response.status_code == 200 and len(response.json()["results"]) <= 5

