from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import (
    CarrierResult,
    RouteOption,
    SearchRequest,
    SearchResponse,
)
from app.services.carrier_search import search_carriers
from app.services.city_validation import (
    US_ONLY_ERROR_MESSAGE,
    is_us_city,
    normalize_us_city,
)
from app.services.route_embed import get_route_options, normalize_city

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search_routes(
    payload: SearchRequest, db: Session = Depends(get_db)
) -> SearchResponse:
    if not is_us_city(payload.from_city, payload.from_lat, payload.from_lng) or not is_us_city(
        payload.to_city, payload.to_lat, payload.to_lng
    ):
        raise HTTPException(status_code=422, detail=US_ONLY_ERROR_MESSAGE)

    from_city = normalize_city(normalize_us_city(payload.from_city))
    to_city = normalize_city(normalize_us_city(payload.to_city))

    carriers = [
        CarrierResult(**carrier)
        for carrier in search_carriers(db, from_city, to_city)
    ]
    routes = [
        RouteOption(**route)
        for route in get_route_options(
            from_city,
            to_city,
            from_lat=payload.from_lat,
            from_lng=payload.from_lng,
            to_lat=payload.to_lat,
            to_lng=payload.to_lng,
        )
    ]

    return SearchResponse(
        from_city=from_city,
        to_city=to_city,
        routes=routes,
        carriers=carriers,
    )
