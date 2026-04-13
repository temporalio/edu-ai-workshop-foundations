# ABOUTME: Tool definitions and implementations for the AI agents exercise.
# ABOUTME: Includes weather alerts, random number, IP address, and geolocation tools.

import json
import random
from typing import Any

import httpx
import requests
from models import (
    GetLocationRequest,
    GetWeatherAlertsRequest,
    oai_responses_tool_from_model,
)

# Constants for the National Weather Service API
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


def _alerts_url(state: str) -> str:
    """Build the NWS API URL for a given state."""
    return f"{NWS_API_BASE}/alerts/active/area/{state}"


async def _make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=5.0)
        response.raise_for_status()
        return response.json()


# Tool implementation functions

async def get_weather_alerts_impl(weather_alerts_request: GetWeatherAlertsRequest) -> str:
    """Get weather alerts for a US state."""
    data = await _make_nws_request(_alerts_url(weather_alerts_request.state))
    return json.dumps(data)


async def get_random_number() -> str:
    """Get a random number between 0 and 100."""
    data = random.randint(0, 100)
    return str(data)


def get_ip_address() -> str:
    """Get the IP address of the current machine."""
    response = requests.get("https://icanhazip.com")
    response.raise_for_status()
    return response.text.strip()


def get_location_info(req: GetLocationRequest) -> str:
    """Get location information for an IP address."""
    response = requests.get(f"http://ip-api.com/json/{req.ipaddress}")
    response.raise_for_status()
    result = response.json()
    return f"{result['city']}, {result['regionName']}, {result['country']}"


# OpenAI tool definitions

WEATHER_ALERTS_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_weather_alerts",
    "Get weather alerts for a US state.",
    GetWeatherAlertsRequest,
)

# TODO: Add a description for the get_random_number tool
# similar to "Get a random number between 0 and 100."
RANDOM_NUMBER_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_random_number",
    "",
    None,
)

# TODO: Add a description for the get_ip_address tool
# similar to "Get the IP address of the current machine."
GET_IP_ADDRESS_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_ip_address",
    "",
    None,
)

# TODO: Add a description for the get_location_info tool
# similar to "Get the location information for an IP address. This includes the city, state, and country."
GET_LOCATION_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_location_info",
    "",
    GetLocationRequest,
)


def get_tools() -> list[dict[str, Any]]:
    """Return all available tools for the agent."""
    # TODO: Add RANDOM_NUMBER_TOOL_OAI, GET_LOCATION_TOOL_OAI, and
    # GET_IP_ADDRESS_TOOL_OAI to the list
    return [
        WEATHER_ALERTS_TOOL_OAI,
    ]
