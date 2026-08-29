from real_estate_ranking.data.pipeline import (
    generate_properties,
    simulate_listings,
    validate_properties,
)
from real_estate_ranking.schemas import SearchRequest
from real_estate_ranking.serving.engine import SearchEngine
from real_estate_ranking.simulation.behavior import (
    generate_users,
    simulate_interactions,
    temporal_split,
)

props, quality = validate_properties(generate_properties(2500)); listings = simulate_listings(props); users = generate_users()
events = simulate_interactions(users, listings); train, validation, test = temporal_split(events)
engine = SearchEngine(listings, users, train)
request = SearchRequest.model_validate({"user_id":"user_000001","search":{"latitude":39.0840,"longitude":-77.1528,
 "radius_miles":15,"min_price":500000,"max_price":800000,"min_bedrooms":3,"property_types":["single_family","townhouse"]},"top_k":10})
response = engine.search(request)
print(f"Market: Montgomery County, MD | properties={len(listings)} events={len(events)} split={len(train)}/{len(validation)}/{len(test)}")
print(f"Quality: {quality} | variant={response.experiment_variant} | latency={response.timings_ms}")
for item in response.results:
    print(f"{item.rank:2}. {item.property_id} ${item.asking_price:,.0f} {item.property_type:13} score={item.score:.3f} {','.join(item.reasons)}")

