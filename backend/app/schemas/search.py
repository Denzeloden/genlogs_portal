from pydantic import BaseModel, Field


class CarrierResult(BaseModel):
    name: str
    trucks_per_day: int


class RouteOption(BaseModel):
    label: str
    duration_text: str
    distance_text: str
    embed_url: str


class SearchRequest(BaseModel):
    from_city: str = Field(..., min_length=1)
    to_city: str = Field(..., min_length=1)


class SearchResponse(BaseModel):
    from_city: str
    to_city: str
    routes: list[RouteOption]
    carriers: list[CarrierResult]
