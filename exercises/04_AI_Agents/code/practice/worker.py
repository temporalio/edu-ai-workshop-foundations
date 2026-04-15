# ABOUTME: Temporal Worker for AI agent workflows with tool-calling and agentic loop modes.
# ABOUTME: Use --agent flag for the agentic loop worker, default is tool-calling only.

import argparse
import asyncio
import concurrent.futures
import logging
import warnings

from activities import create, dynamic_tool_activity, get_weather_alerts
from agent_workflow import AgentWorkflow
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker
from tool_calling_workflow import ToolCallingWorkflow


async def run_tool_calling_worker() -> None:
    """Run the worker for the simple tool-calling workflow."""
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as activity_executor:
        worker = Worker(
            client,
            # TODO: Set task_queue to "exercise-04-tool-calling"
            task_queue="",
            # TODO: Add ToolCallingWorkflow to the workflows list
            workflows=[],
            activities=[create, get_weather_alerts],
            activity_executor=activity_executor,
        )
        logging.info("Starting tool-calling worker...")
        await worker.run()


async def run_agent_worker() -> None:
    """Run the worker for the agentic loop workflow with dynamic activities."""
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as activity_executor:
        worker = Worker(
            client,
            # TODO: Set task_queue to "exercise-04-agent"
            task_queue="",
            # TODO: Add AgentWorkflow to the workflows list
            workflows=[],
            # TODO: Add create and dynamic_tool_activity to the activities list
            activities=[],
            activity_executor=activity_executor,
        )
        logging.info("Starting agent worker...")
        await worker.run()


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    logging.getLogger("temporalio").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    warnings.filterwarnings("ignore", category=UserWarning, module="temporalio.converter")

    parser = argparse.ArgumentParser(description="Run AI Agent Worker")
    parser.add_argument("--agent", action="store_true", help="Run the agentic loop worker instead of tool-calling")
    args = parser.parse_args()

    if args.agent:
        asyncio.run(run_agent_worker())
    else:
        asyncio.run(run_tool_calling_worker())


if __name__ == "__main__":
    main()
