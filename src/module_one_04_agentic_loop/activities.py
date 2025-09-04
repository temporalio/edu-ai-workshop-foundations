import inspect
import json
import os
import sys
from typing import Sequence

from temporalio import activity, workflow
import temporalio.common

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

with workflow.unsafe.imports_passed_through():
    from litellm import completion
    from config import OPENAI_API_KEY

from models import ToolDefinition, AgentGoal


class AgentActivities:
    
    @activity.defn
    async def agent_validate_prompt(
        self,
        agent_goal: AgentGoal,
        user_prompt: str
    ) -> bool:
        """Validate that the user's prompt aligns with the agent's capabilities.
        
        This ensures the request matches what the agent can do with its available tools.
        """
        # Build a description of what the agent can do
        capabilities = f"Agent: {agent_goal.agent_name}\n"
        capabilities += f"Purpose: {agent_goal.description}\n"
        capabilities += "Available tools:\n"
        for tool in agent_goal.tools:
            capabilities += f"  - {tool.name}: {tool.description}\n"
        
        validation_prompt = f"""Given this agent's capabilities:
{capabilities}

And this user request:
"{user_prompt}"

Can this agent fulfill this request with its available tools? 
Respond with only YES or NO."""
        
        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": validation_prompt}],
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        
        result = response.choices[0].message.content.strip().upper()
        activity.logger.info(f"Prompt validation result: {result}")
        
        return "YES" in result
    
    @activity.defn
    async def ai_select_tool_with_params(
        self,
        goal: str | AgentGoal,  # Can accept either a string or AgentGoal
        available_tools: dict[str, ToolDefinition], 
        context: str
    ) -> dict[str, str | dict[str, str | int]]:
        """AI agent selects tool AND extracts parameters in one call.
        """
        if isinstance(goal, AgentGoal):
            agent_goal = goal
            goal_text = agent_goal.description
            # Use the agent's tools if provided, otherwise use passed tools
            if agent_goal.tools:
                tools_to_use = {tool.name: tool for tool in agent_goal.tools}
            else:
                tools_to_use = available_tools
        else:
            agent_goal = None
            goal_text = goal
            tools_to_use = available_tools
        
        # Build tool descriptions with parameters
        tools_description = []
        for name, tool_def in tools_to_use.items():
            if isinstance(tool_def, ToolDefinition):
                tool_str = f"Tool: {name}\n"
                tool_str += f"Description: {tool_def.description}\n"
                tool_str += "Arguments: " + ", ".join(
                    [f"{arg.name} ({arg.type}): {arg.description}" for arg in tool_def.arguments]
                )
                tools_description.append(tool_str)
        
        tools_text = "\n\n".join(tools_description)
        
        # Build prompt with optional AgentGoal context
        if agent_goal:
            # Use richer context from AgentGoal
            prompt = f"""{agent_goal.starter_prompt if agent_goal.starter_prompt else ''}

You are {agent_goal.agent_name if agent_goal.agent_name else 'an AI agent'}.
Goal: {goal_text}

{f"Example interactions: {agent_goal.example_conversation_history}" if agent_goal.example_conversation_history else ""}

Available tools:
{tools_text}

Current context:
{context if context else "Just starting - no actions taken yet"}

Based on the goal and context, decide the next action.
Return a JSON object with:
- "tool": the tool name to use (or "DONE" if complete)  
- "parameters": an object with the required parameters

Return ONLY the JSON object."""
        else:
            # Simple prompt for string goal
            prompt = f"""You are an AI agent working to achieve this goal: {goal_text}

Available tools:
{tools_text}

Current context:
{context if context else "Just starting - no actions taken yet"}

Based on the goal and context, decide the next action.
Return a JSON object with:
- "tool": the tool name to use (or "DONE" if complete)
- "parameters": an object with the required parameters

Examples:
{{"tool": "search_flights", "parameters": {{"origin": "NYC", "destination": "London", "date": "March 15"}}}}
{{"tool": "book_flight", "parameters": {{"flight_id": "AA123", "seat_class": "economy"}}}}
{{"tool": "DONE", "parameters": {{}}}}

Return ONLY the JSON object."""
        
        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        
        decision_text = response.choices[0].message.content.strip()
        activity.logger.info(f"AI decision: {decision_text}")
        
        try:
            return json.loads(decision_text)
        except json.JSONDecodeError:
            if "DONE" in decision_text.upper():
                return {"tool": "DONE", "parameters": {}}
            return {"tool": decision_text, "parameters": {}}

@activity.defn(dynamic=True)
async def dynamic_tool_activity(args: Sequence[temporalio.common.RawValue]) -> str:
    """Dynamic activity handler that executes tools based on activity type.

    This activity is called dynamically when the workflow executes an activity
    with an unknown activity type. It looks up the tool handler from the registry
    and executes it with the provided arguments.
    """
    from tools import get_handler
    
    # Get the activity type which will be our tool name
    tool_name = activity.info().activity_type
    
    # Extract the arguments from the raw value
    tool_args = activity.payload_converter().from_payload(args[0].payload, dict)
    
    activity.logger.info(f"Running dynamic tool '{tool_name}' with args: {tool_args}")
    
    # Delegate to the relevant function
    handler = get_handler(tool_name)
    if inspect.iscoroutinefunction(handler):
        result = await handler(tool_args)
    else:
        result = handler(tool_args)
    
    activity.logger.info(f"Tool '{tool_name}' result: {result}")
    return result

agent_activities = AgentActivities()

# Create standalone activity functions that wrap the class methods
@activity.defn(name="agent_validate_prompt")
async def agent_validate_prompt(agent_goal: AgentGoal, user_prompt: str) -> bool:
    """Standalone activity function that delegates to the class method."""
    return await agent_activities.agent_validate_prompt(agent_goal, user_prompt)

@activity.defn(name="ai_select_tool_with_params") 
async def ai_select_tool_with_params(
    goal: str | AgentGoal,
    available_tools: dict[str, ToolDefinition],
    context: str
) -> dict[str, str | dict[str, str | int]]:
    """Standalone activity function that delegates to the class method."""
    return await agent_activities.ai_select_tool_with_params(goal, available_tools, context)