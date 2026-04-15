# ABOUTME: Temporal Worker that polls for and executes workflow and activity tasks.
# ABOUTME: Registers the GenerateReportWorkflow and all activities on the exercise-02-durability task queue.

import asyncio
import concurrent.futures
import logging
import warnings

from activities import create_pdf, generate_ai_image, llm_call
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import GenerateReportWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Reduce noise from various libraries
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("temporalio").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Suppress Pydantic converter warning
    warnings.filterwarnings("ignore", category=UserWarning, module="temporalio.converter")

    client = await Client.connect("localhost:7233", namespace="default")

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
            client,
            task_queue="exercise-02-durability",
            workflows=[GenerateReportWorkflow],
            activities=[llm_call, create_pdf, generate_ai_image],
            activity_executor=activity_executor,
        )
        logging.info("Starting the worker....")
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
