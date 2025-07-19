from fastapi import APIRouter

from app.api.services import weather

service_api_router = APIRouter()
service_api_router.include_router(weather.router, prefix="/v1/weather", tags=["weather"])

