import asyncio
import uuid
from dotenv import load_dotenv
from models import GenerateReportInput, UserDecision, UserDecisionSignal
from temporalio.client import Client
from workflow import GenerateReportWorkflow
from temporalio.common import WorkflowIDConflictPolicy

async def main() -> None:
    client = await Client.connect("localhost:7233")

    print("Welcome to the Research Report Generator!")
    user_input = input(
        "Enter your research topic or question, OR paste an existing workflow ID (UUID): "
    ).strip()

    if not user_input:
        prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
        workflow_id = f"generate-research-report-workflow-{uuid.uuid4()}"
        print(f"No input provided. Using default prompt: {prompt}")
    else:
        try:
            uuid.UUID(user_input)
            workflow_id = "generate-research-report-workflow-" + user_input
            prompt = "continue"
            print(f"Using provided workflow ID: {workflow_id}. Prompt set to 'continue'.")
        except ValueError:
            prompt = user_input
            workflow_id = f"generate-research-report-workflow-{uuid.uuid4()}"
            print("Using provided prompt.")

    handle = await client.start_workflow(
        GenerateReportWorkflow,
        GenerateReportInput(prompt=prompt),
        id=workflow_id,
        task_queue="durable",
        id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING
    )

    print(f"Workflow ID: {handle.id}, RunID {handle.result_run_id}")

    signal_task = asyncio.create_task(send_user_decision_signal(client, handle.id))

    try:
        result = await handle.result()
        signal_task.cancel()
        print(f"Result: {result}")
    except Exception as e:
        signal_task.cancel()
        print(f"Workflow failed: {e}")


async def query_research_result(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)

    try:
        research_result = await handle.query(GenerateReportWorkflow.get_research_result)
        if research_result:
            print(f"Research Result: {research_result}")
        else:
            print("Research Result: Not yet available")

    except Exception as e:
        print(f"Query failed: {e}")


async def send_user_decision_signal(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)

    while True:
        print("\n" + "=" * 50)
        print("Research is in progress! When it's complete you can choose one of the following options:")
        print("1. Type 'query' to query for research result. If querying, wait for `Reserch Complete` to appear in terminal window with Worker running first.")
        print("2. Type 'keep' to approve the research and create PDF")
        print("3. Type 'edit' to modify the research")
        print("=" * 50)

        decision = input("Your decision (query/keep/edit): ").strip().lower()

        if decision in {"query", "1"}:
            await query_research_result(client, workflow_id)
        if decision in {"keep", "2"}:
            signal_data = UserDecisionSignal(decision=UserDecision.KEEP)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to keep research and create PDF")
            break
        elif decision in {"edit", "3"}:
            additional_prompt_input = input("Enter additional instructions for the research (optional): ").strip()
            additional_prompt = additional_prompt_input if additional_prompt_input else ""

            signal_data = UserDecisionSignal(decision=UserDecision.EDIT, additional_prompt=additional_prompt)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to regenerate research")

        else:
            print("Please enter either 'keep', 'edit', or 'query'")


if __name__ == "__main__":
    asyncio.run(main())
