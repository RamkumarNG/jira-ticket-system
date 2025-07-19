import os
import httpx

from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.utils.http_client import AsyncHTTPClient
from app.schema.services.weather import GetWeatherResponse, WeatherInfo
from app.schema.v1.common import RequestStatus


router = APIRouter()

client = AsyncHTTPClient(settings.WEATHER_API_ENDPOINT)

@router.get("")
async def fetch_weather(request: Request, city: str) -> GetWeatherResponse:
    try:
        response = await client.get("weather", params={
            "q": city,
            "appid": settings.OPEN_WEATHER_API_KEY,
            "units": "metric"
        })

        weatherInfo = WeatherInfo(
            city=response["name"],
            temperature=response["main"]["temp"],
            weather=response["weather"][0]["description"],
            humidity=response["main"]["humidity"],
            wind_speed=response["wind"]["speed"]
        )
    
        response = GetWeatherResponse (
            request_id = request.state.id,
            status =  RequestStatus.success,
            message = "Weather data fetched successfully",
            data = weatherInfo
        )

        return JSONResponse(
            jsonable_encoder(response),
            status_code=status.HTTP_200_OK
        )
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failure",
                "message": f"An unexpected error occurred: {str(e)}",
                "request_id": request.state.id
            }
        )
