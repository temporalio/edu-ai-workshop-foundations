import json
from temporalio import activity
from litellm import completion
from models import ToolDefinition, AgentGoal

@activity.defn
async def agent_validate_prompt(
    agent_goal: AgentGoal,
    user_prompt: str,
    llm_model: str,
    llm_api_key: str
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
            model=llm_model,
            messages=[{"role": "user", "content": validation_prompt}],
            temperature=0.1,
            api_key=llm_api_key
        )
        
        result = response.choices[0].message.content.strip().upper()
        activity.logger.info(f"Prompt validation result: {result}")
        
        return "YES" in result


@activity.defn
async def ai_select_tool_with_params(
    goal: str,
    available_tools: dict[str, ToolDefinition], 
    context: str,
    llm_model: str,
    llm_api_key: str
) -> dict[str, str | dict[str, str | int]]:
    """AI agent selects tool and extracts parameters"""
    
    # Build tool descriptions
    tools_text = "\n\n".join([
        f"Tool: {name}\n"
        f"Description: {tool.description}\n"
        f"Arguments: {', '.join(f'{arg.name} ({arg.type}): {arg.description}' for arg in tool.arguments)}"
        for name, tool in available_tools.items()
    ])

    # Build prompt
    prompt = f"""You are a flight-booking AI agent working to achieve this goal: {goal}

Available tools:
{tools_text}

Current context:
{context or "Just starting - no actions taken yet"}

Based on the goal and context, decide the next action.
Return a JSON object with:
- "tool": the tool name to use (or "DONE" if complete)
- "parameters": an object with the required parameters

Examples:
{{"tool": "search_flights", "parameters": {{"origin": "NYC", "destination": "London", "date": "tomorrow"}}}}
{{"tool": "book_flight", "parameters": {{"flight_id": "UA456", "seat_class": "economy"}}}}
{{"tool": "DONE", "parameters": {{}}}}

Return ONLY the JSON object."""

    response = completion(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        api_key=llm_api_key
    )

    decision_text = response.choices[0].message.content.strip()
    activity.logger.info(f"AI decision: {decision_text}")

    try:
        return json.loads(decision_text)
    except json.JSONDecodeError:
        activity.logger.warning(f"Failed to parse: {decision_text}")
        return {"tool": "DONE", "parameters": {}}