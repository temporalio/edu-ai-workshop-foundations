import concurrent.futures
from temporalio.client import Client
from temporalio.worker import Worker

async def run_worker() -> None:
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233", namespace="default")

    # Run the Worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
            client,
            task_queue="research",
            workflows=[GenerateReportWorkflow],
            activities=[llm_call, create_pdf_activity],
            activity_executor=activity_executor
        )

        print(f"Starting the worker....")
        await worker.run()