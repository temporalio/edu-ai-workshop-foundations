import asyncio

from temporalio.client import Client

# Create client connected to server at the given address
client = await Client.connect("localhost:7233", namespace="default")

print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ").strip()

if not prompt:
    prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {prompt}")

# Asynchronous start of a Workflow
handle = await client.start_workflow(
    GenerateReportWorkflow.run,
    GenerateReportInput(prompt=prompt),
    id="generate-research-report-workflow", # user-defined Workflow identifier, which typically has some business meaning
    task_queue="research", # the task-queue that your Worker is polling
)

print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")