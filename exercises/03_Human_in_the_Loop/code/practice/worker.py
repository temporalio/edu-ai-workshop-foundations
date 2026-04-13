# ABOUTME: Temporal Worker for the human-in-the-loop research report generator.
# ABOUTME: Registers the workflow and all activities including image generation.

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

    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("temporalio").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    warnings.filterwarnings("ignore", category=UserWarning, module="temporalio.converter")

    client = await Client.connect("localhost:7233", namespace="default")

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
            client,
            task_queue="exercise-03-human-in-the-loop",
            workflows=[GenerateReportWorkflow],
            # TODO: Add generate_ai_image to the activities list
            activities=[llm_call, create_pdf],
            activity_executor=activity_executor,
        )
        logging.info("Starting the worker....")
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
