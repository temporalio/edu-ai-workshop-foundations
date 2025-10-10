from temporalio.client import Client
import uuid

# Create client connected to server at the given address
client = await Client.connect("localhost:7233", namespace="default")

print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ").strip()

if not prompt:
    prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {prompt}")

# Asynchronous start of a Workflow
handle = await client.start_workflow(
    GenerateReportWorkflow,
    GenerateReportInput(prompt=prompt),
    id=f"generate-research-report-workflow-{uuid.uuid4()}",
    task_queue="research",
)

print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")