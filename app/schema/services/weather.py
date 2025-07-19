from pydantic import BaseModel
from app.schema.v1.common import ResponseStructure


class WeatherInfo(BaseModel):
    city: str
    temperature: float
    weather: str
    humidity: int
    wind_speed: float

class GetWeatherResponse(ResponseStructure):
    data: WeatherInfo
