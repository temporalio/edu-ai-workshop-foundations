from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BookingRequest:
    goal: str
    

@dataclass
class BookingResult:
    message: str  # Summary of what was accomplished
    steps_taken: list[str]  # List of steps the AI took


@dataclass
class ToolArgument:
    name: str
    type: str
    description: str


@dataclass
class ToolDefinition:
    name: str
    description: str
    arguments: list[ToolArgument]


@dataclass
class AgentGoal:
    """Defines an agent's goal, available tools, and context for execution."""
    agent_name: str
    tools: List[ToolDefinition]
    description: str
    starter_prompt: str
    example_conversation_history: Optional[str] = ""
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None