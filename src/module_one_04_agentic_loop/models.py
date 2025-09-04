from dataclasses import dataclass
from typing import List, Union, Optional


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
    
    
@dataclass
class AgentDecision:
    """Represents an agent's decision about which tool to use."""
    tool: str
    parameters: dict[str, Union[str, int]]
    reasoning: Optional[str] = None  # Why the agent chose this tool