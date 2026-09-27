import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from real_estate_ranking.data.pipeline import (
    generate_properties,
    simulate_listings,
    validate_properties,
)
from real_estate_ranking.events.publishers import LocalEventPublisher, LocalWorkflowQueue
from real_estate_ranking.schemas import InteractionEvent, SearchRequest, SearchResponse
from real_estate_ranking.serving.engine import SearchEngine
from real_estate_ranking.simulation.behavior import generate_users

properties, _ = validate_properties(generate_properties(1800))
engine = SearchEngine(simulate_listings(properties), generate_users())
publisher = LocalEventPublisher(Path("data/events/interactions.jsonl"))
workflows = LocalWorkflowQueue()
app = FastAPI(title="Personalized Real-Estate Ranking API", version="0.1.0")
logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def structured_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error on %s", request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred"},
                                                  "request_path": request.url.path})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    return engine.search(request)


@app.post("/v1/events", status_code=202)
def events(event: InteractionEvent) -> dict[str, object]:
    return {"accepted": publisher.publish(event), "event_id": event.event_id}


@app.post("/v1/properties/{property_id}/tour", status_code=202)
def tour(property_id: str, user_id: str = Query(min_length=1)) -> dict[str, str]:
    if property_id not in set(engine.listings.property_id):
        raise HTTPException(404, "property not found")
    return {"message_id": workflows.enqueue("tour", property_id, user_id)}


@app.post("/v1/properties/{property_id}/contact", status_code=202)
def contact(property_id: str, user_id: str = Query(min_length=1)) -> dict[str, str]:
    if property_id not in set(engine.listings.property_id):
        raise HTTPException(404, "property not found")
    return {"message_id": workflows.enqueue("contact", property_id, user_id)}
