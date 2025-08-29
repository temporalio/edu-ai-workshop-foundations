import asyncio
import concurrent.futures
import logging
import warnings

from activities import create_pdf, llm_call
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import GenerateReportWorkflow

warnings.filterwarnings("ignore", message="If you're using Pydantic v2*")

# Set logging levels to reduce verbosity
logging.getLogger('temporalio').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# Keep only your application's INFO logs
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)

    client = await Client.connect("localhost:7233", namespace="default")

    # Run the Worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker: Worker = Worker(
            client,
            task_queue="durable",
            workflows=[GenerateReportWorkflow],
            activities=[llm_call, create_pdf],
            activity_executor=activity_executor,
        )
        logging.info("Starting the worker....")
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
