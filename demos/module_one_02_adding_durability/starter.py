import asyncio
import os

from dotenv import load_dotenv
from models import GenerateReportInput
from temporalio.client import Client
from workflow import GenerateReportWorkflow

load_dotenv(override=True)

# Get LLM_API_KEY environment variable
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", "YOU-DIDNT-PROVIDE-A-KEY")

async def main() -> None:
    client = await Client.connect("localhost:7233")

    print("Welcome to the Research Report Generator!")
    prompt = input("Enter your research topic or question: ").strip()

    if not prompt:
        prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
        print(f"No prompt entered. Using default: {prompt}")

    research_input = GenerateReportInput(prompt=prompt, llm_api_key=LLM_API_KEY)

    handle = await client.start_workflow(
        GenerateReportWorkflow.run,
        research_input,
        id="generate-research-report-workflow",
        task_queue="durable",
    )

    print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")
    result = await handle.result()
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
