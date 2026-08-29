from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class Provenance(StrEnum):
    PUBLIC_SOURCE = "PUBLIC_SOURCE"
    DERIVED_PUBLIC = "DERIVED_PUBLIC"
    SIMULATED = "SIMULATED"
    MODEL_GENERATED = "MODEL_GENERATED"


class SearchCriteria(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_miles: float = Field(gt=0, le=100)
    min_price: float = Field(ge=0)
    max_price: float = Field(gt=0)
    min_bedrooms: int = Field(default=0, ge=0, le=20)
    min_bathrooms: float = Field(default=0, ge=0, le=20)
    property_types: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_range(self) -> "SearchCriteria":
        if self.min_price > self.max_price:
            raise ValueError("min_price cannot exceed max_price")
        return self


class SearchContext(BaseModel):
    device: str = "web"
    session_id: str = Field(default_factory=lambda: f"session_{uuid4().hex[:12]}")


class SearchRequest(BaseModel):
    user_id: str
    search: SearchCriteria
    context: SearchContext = Field(default_factory=SearchContext)
    top_k: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    property_id: str
    listing_id: str
    rank: int
    score: float
    distance_miles: float
    asking_price: float
    property_type: str
    bedrooms: int
    reasons: list[str]


class SearchResponse(BaseModel):
    request_id: str
    model_version: str
    experiment_variant: str
    results: list[SearchResult]
    timings_ms: dict[str, float]


class InteractionEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    property_id: str
    listing_id: str
    search_id: str
    session_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    position: int = Field(ge=1)
    experiment_id: str = "ranking_v1"
    variant: str = "control"
    device: str = "web"
    schema_version: str = "1.0"
    exposure_propensity: float = Field(gt=0, le=1)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))

    def record(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

