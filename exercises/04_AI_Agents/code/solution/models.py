# ABOUTME: Data models and helper functions for the AI agents exercise.
# ABOUTME: Defines request types, tool schema helpers, and agent system instructions.

from dataclasses import dataclass
from typing import Any

from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel, Field


@dataclass
class OpenAIResponsesRequest:
    model: str
    instructions: str
    input: object
    tools: list[dict[str, Any]]


class GetWeatherAlertsRequest(BaseModel):
    state: str = Field(description="Two-letter US state code (e.g. CA, NY)")


class GetLocationRequest(BaseModel):
    ipaddress: str = Field(description="An IP address")


def oai_responses_tool_from_model(
    name: str, description: str, model: type[BaseModel] | None,
) -> dict[str, Any]:
    """Convert a Pydantic model into an OpenAI Responses API tool definition."""
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": (
            to_strict_json_schema(model)
            if model
            else {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        ),
        "strict": True,
    }


HELPFUL_AGENT_SYSTEM_INSTRUCTIONS = """
You are a helpful agent that can use tools to help the user.
You will be given a task and a list of tools to use.
You may or may not need to use the tools to complete the task.
If no tools are needed, respond in haikus.
"""
