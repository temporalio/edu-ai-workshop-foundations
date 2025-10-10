import concurrent.futures
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.pydantic import pydantic_data_converter

async def run_worker() -> None:
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233", data_converter=pydantic_data_converter)

    # Run the Worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
            client,
            task_queue="tool-calling-python-task-queue",
            workflows=[ToolCallingWorkflow],
            activities=[create, get_weather_alerts],
            activity_executor=activity_executor
        )

        print(f"Starting the worker....")
        await worker.run()