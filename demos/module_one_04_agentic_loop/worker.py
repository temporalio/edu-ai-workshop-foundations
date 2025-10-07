import asyncio
import concurrent.futures
import logging

from activities import (
    agent_validate_prompt,
    ai_select_tool_with_params,
)
from tools import (
    search_flights,
    check_seat_availability,
    calculate_total_cost,
    book_flight,
    send_confirmation,
)
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import AgenticWorkflow

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    client = await Client.connect("localhost:7233")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as activity_executor:
        worker = Worker(
            client,
            task_queue="agentic-queue",
            workflows=[AgenticWorkflow],
            activities=[
                agent_validate_prompt,
                ai_select_tool_with_params,
                search_flights,
                check_seat_availability,
                calculate_total_cost,
                book_flight,
                send_confirmation,
            ],
            activity_executor=activity_executor,
        )
        logging.info("Starting the worker....")
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())