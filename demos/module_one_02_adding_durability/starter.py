import asyncio
import uuid
from models import GenerateReportInput
from temporalio.client import Client
from workflow import GenerateReportWorkflow

async def main() -> None:
    client = await Client.connect("localhost:7233")

    print("Welcome to the Research Report Generator!")
    prompt = input("Enter your research topic or question: ").strip()

    if not prompt:
        prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
        print(f"No prompt entered. Using default: {prompt}")

    research_input = GenerateReportInput(prompt=prompt)

    handle = await client.start_workflow(
        GenerateReportWorkflow,
        research_input,
        id=f"generate-researdch-report-workflow-{uuid.uuid4()}",
        task_queue="durable",
    )

    print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")
    result = await handle.result()
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
