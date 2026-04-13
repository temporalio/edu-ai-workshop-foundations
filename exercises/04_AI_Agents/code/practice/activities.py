# ABOUTME: Temporal Activity definitions for OpenAI API calls and dynamic tool dispatch.
# ABOUTME: Includes the create activity for LLM calls and dynamic_tool_activity for tool execution.

import inspect
from typing import Sequence

from models import (
    GetLocationRequest,
    GetWeatherAlertsRequest,
    OpenAIResponsesRequest,
)
from openai import AsyncOpenAI
from openai.types.responses import Response
from pydantic import BaseModel
from temporalio import activity
from temporalio.common import RawValue
from tools import (
    get_ip_address,
    get_location_info,
    get_random_number,
    get_weather_alerts_impl,
)


@activity.defn
async def create(request) -> Response:
    # TODO: Add the type annotation OpenAIResponsesRequest to the request parameter above
    """Call the OpenAI Responses API with the given request."""
    # Temporal best practice: Disable retry logic in OpenAI API client library.
    client = AsyncOpenAI(max_retries=0)

    resp = await client.responses.create(
        model=request.model,
        instructions=request.instructions,
        input=request.input,
        tools=request.tools,
        timeout=30,
    )

    return resp


@activity.defn
async def get_weather_alerts(weather_alerts_request: GetWeatherAlertsRequest) -> str:
    """Get weather alerts for a US state via the National Weather Service API."""
    # TODO: Call the get_weather_alerts_impl function with weather_alerts_request
    # and return the result. Don't forget to await it.
    return ""


def get_handler(tool_name: str):
    """Look up the handler function for a given tool name."""
    if tool_name == "get_location_info":
        return get_location_info
    if tool_name == "get_ip_address":
        return get_ip_address
    if tool_name == "get_weather_alerts":
        return get_weather_alerts_impl
    if tool_name == "get_random_number":
        return get_random_number
    return None


# TODO: Add the @activity.defn(dynamic=True) decorator to this function
async def dynamic_tool_activity(args: Sequence[RawValue]) -> dict:
    """Dynamically execute any registered tool based on the activity name."""
    # TODO: Get the tool name from activity.info().activity_type
    tool_name = ""

    # Convert the raw Temporal payload to a Python dictionary
    tool_args = activity.payload_converter().from_payload(args[0].payload, dict)
    activity.logger.info(f"Running dynamic tool '{tool_name}' with args: {tool_args}")

    # TODO: Get the handler function using get_handler(tool_name)
    handler = get_handler(tool_name)
    if not handler:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Inspect the handler's function signature to see what parameters it expects
    sig = inspect.signature(handler)
    params = list(sig.parameters.values())

    if len(params) == 0:
        call_args = []
    else:
        # If the handler expects a Pydantic model, convert the dict to that model
        ann = params[0].annotation
        if isinstance(tool_args, dict) and isinstance(ann, type) and issubclass(ann, BaseModel):
            call_args = [ann(**tool_args)]
        else:
            call_args = [tool_args]

    result = await handler(*call_args) if inspect.iscoroutinefunction(handler) else handler(*call_args)

    activity.logger.info(f"Tool '{tool_name}' result: {result}")
    return result
