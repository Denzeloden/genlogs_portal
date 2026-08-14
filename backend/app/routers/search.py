from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import (
    CarrierResult,
    RouteOption,
    SearchRequest,
    SearchResponse,
)
from app.services.carrier_search import search_carriers
from app.services.route_embed import get_route_options, normalize_city

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search_routes(
    payload: SearchRequest, db: Session = Depends(get_db)
) -> SearchResponse:
    from_city = normalize_city(payload.from_city)
    to_city = normalize_city(payload.to_city)

    carriers = [
        CarrierResult(**carrier)
        for carrier in search_carriers(db, from_city, to_city)
    ]
    routes = [RouteOption(**route) for route in get_route_options(from_city, to_city)]

    return SearchResponse(
        from_city=from_city,
        to_city=to_city,
        routes=routes,
        carriers=carriers,
    )
