import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

async def run_worker() -> None:
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    worker = Worker(
        client,
        task_queue="tool-calling-python-task-queue",
        workflows=[
            ToolCallingWorkflow,
        ],
        activities=[
            create,
            get_weather_alerts.get_weather_alerts,
        ],
    )
    
    print(f"Starting the worker....")
    await worker.run()