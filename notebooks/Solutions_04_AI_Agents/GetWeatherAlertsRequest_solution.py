from pydantic import BaseModel

class GetWeatherAlertsRequest(BaseModel):
    state: str = Field(description="Two-letter US state code (e.g. CA, NY)")

WEATHER_ALERTS_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_weather_alerts",
    "Get weather alerts for a US state.",
    GetWeatherAlertsRequest)