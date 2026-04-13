# ABOUTME: Client script that starts tool-calling or agent workflows on Temporal.
# ABOUTME: Use --agent flag for the agentic loop, default is tool-calling.

import argparse
import asyncio
import uuid

from agent_workflow import AgentWorkflow
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from tool_calling_workflow import ToolCallingWorkflow


async def run_tool_calling(query: str) -> None:
    """Start the tool-calling workflow and print the result."""
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    result = await client.execute_workflow(
        ToolCallingWorkflow,
        query,
        id=f"tool-calling-workflow-{uuid.uuid4()}",
        task_queue="exercise-04-tool-calling",
    )
    print(f"Result: {result}")


async def run_agent(query: str) -> None:
    """Start the agentic loop workflow and print the result."""
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    result = await client.execute_workflow(
        AgentWorkflow,
        query,
        id=f"agent-workflow-{uuid.uuid4()}",
        task_queue="exercise-04-agent",
    )
    print(f"Result: {result}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI Agent Workflow")
    parser.add_argument("--agent", action="store_true", help="Run the agentic loop instead of tool-calling")
    parser.add_argument("query", nargs="?", default=None, help="The query to send to the agent")
    args = parser.parse_args()

    query = args.query
    if not query:
        if args.agent:
            query = "What's the weather like where I am right now?"
        else:
            query = "What are the weather alerts in California?"

    print(f"Query: {query}")

    if args.agent:
        asyncio.run(run_agent(query))
    else:
        asyncio.run(run_tool_calling(query))


if __name__ == "__main__":
    main()
