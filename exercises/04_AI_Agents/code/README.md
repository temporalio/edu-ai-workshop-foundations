# Exercise 4: AI Agents

Build tool-calling and agentic loop workflows with Temporal and the OpenAI Responses API.

## Prerequisites

- Temporal server running (`temporal server start-dev`)
- An **OpenAI API key** set as the `OPENAI_API_KEY` environment variable (this exercise uses the OpenAI Responses API directly, not litellm)

## Overview

This exercise has two parts:

**Part A: Tool-Calling Workflow** — A single LLM call with one tool (weather alerts). The LLM decides whether to use the tool, and if so, the workflow executes it and returns a formatted result.

**Part B: Agentic Loop Workflow** — A multi-turn loop where the LLM has access to multiple tools (weather, random number, IP, location). It reasons about which tools to call and loops until the task is complete, using dynamic activities for tool dispatch.

## Instructions

### Part 1: Complete the Models

Open `practice/models.py`:
- Add the description `"Two-letter US state code (e.g. CA, NY)"` to the `GetWeatherAlertsRequest.state` field

### Part 2: Add Tool Descriptions

Open `practice/tools.py`:
1. Add descriptions for `RANDOM_NUMBER_TOOL_OAI`, `GET_IP_ADDRESS_TOOL_OAI`, and `GET_LOCATION_TOOL_OAI`
2. Add the three additional tools to the `get_tools()` return list

### Part 3: Complete the Activities

Open `practice/activities.py`:
1. Add `OpenAIResponsesRequest` as the type annotation for the `create` activity's `request` parameter
2. In `get_weather_alerts`, call `get_weather_alerts_impl` with the request and return the result
3. Add the `@activity.defn(dynamic=True)` decorator to `dynamic_tool_activity`
4. Set `tool_name` to `activity.info().activity_type`

### Part 4: Complete the Tool-Calling Workflow

Open `practice/tool_calling_workflow.py`:
1. Fill in the `OpenAIResponsesRequest` fields: `instructions`, `input`, and `tools`
2. Add the `get_weather_alerts` activity call with `GetWeatherAlertsRequest`

### Part 5: Run the Tool-Calling Workflow

```bash
# Terminal 1:
uv run worker.py

# Terminal 2:
uv run starter.py "What are the weather alerts in California?"
```

### Part 6: Complete the Agent Workflow

Open `practice/agent_workflow.py`:
1. Change `while False` to `while True` to enable the agentic loop
2. Set the `item.type` comparison to `"function_call"`
3. In `_handle_function_call`, execute a dynamic activity using `item.name`

### Part 7: Complete the Worker and Starter

Open `practice/worker.py`:
1. Set task queues: `"exercise-04-tool-calling"` and `"exercise-04-agent"`
2. Register `ToolCallingWorkflow` and `AgentWorkflow` in their respective workers
3. Register `create` and `dynamic_tool_activity` for the agent worker

Open `practice/starter.py`:
1. Set the matching task queues
2. Replace `ToolCallingWorkflow` with `AgentWorkflow` in the `run_agent` function

### Part 8: Run the Agent Workflow

```bash
# Terminal 1:
uv run worker.py --agent

# Terminal 2:
uv run starter.py --agent "What's the weather like where I am right now?"
```

Watch the agent determine it needs your IP, then your location, then weather alerts — all orchestrated durably by Temporal.

## Running the Exercise

### Tool-Calling Mode
```bash
cd code/04_ai_agents/practice

# Terminal 1: Worker
uv run worker.py

# Terminal 2: Starter
uv run starter.py "What are the weather alerts in Texas?"
```

### Agent Mode
```bash
cd code/04_ai_agents/practice

# Terminal 1: Worker
uv run worker.py --agent

# Terminal 2: Starter
uv run starter.py --agent "What's the weather like where I am?"
```

## Key Concepts

- **Dynamic Activities**: `@activity.defn(dynamic=True)` lets the LLM choose which tool to call at runtime
- **Pydantic Data Converter**: Required for serializing OpenAI Response objects through Temporal
- **Agentic Loop**: The workflow loops until the LLM decides no more tools are needed
- **Tool Dispatch**: The `get_handler` registry maps tool names to implementation functions

## Hints

If you get stuck, check the `solution/` directory for the completed code.
