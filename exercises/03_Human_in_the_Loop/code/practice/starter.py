# ABOUTME: Client script that starts the workflow and interacts via signals and queries.
# ABOUTME: Supports keep/edit decisions, filename input, and research stats queries.

import asyncio
import uuid

from models import FilenameSave, GenerateReportInput, UserDecision, UserDecisionSignal
from temporalio.client import Client
from workflow import GenerateReportWorkflow


async def send_user_decision_signal(client: Client, workflow_id: str) -> None:
    """Interactive loop to send keep/edit signals to the running workflow."""
    handle = client.get_workflow_handle(workflow_id)
    loop = asyncio.get_running_loop()

    while True:
        print("\n" + "=" * 80)
        print("Calling LLM! See the response in your Web UI in the output of the `llm_call` Activity.")
        print("Would you like to keep or edit it?")
        print("1. Type 'keep' to approve the output and create PDF")
        print("2. Type 'edit' to modify the output")
        print("=" * 80)

        decision = await loop.run_in_executor(None, input, "Your decision (keep/edit): ")
        decision = decision.strip().lower()

        if decision in {"keep", "1"}:
            signal_data = UserDecisionSignal(decision=UserDecision.KEEP)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to keep output and create PDF")
            break
        elif decision in {"edit", "2"}:
            additional_prompt_input = input("Enter additional instructions to edit the output (optional): ").strip()
            additional_prompt = additional_prompt_input if additional_prompt_input else ""
            signal_data = UserDecisionSignal(decision=UserDecision.EDIT, additional_prompt=additional_prompt)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to regenerate research")
        else:
            print("Please enter either 'keep' or 'edit'")

    # Filename signal with 20-second timeout
    print(
        "\nWhat do you want to name the file? You have 20 seconds to respond, "
        "otherwise the file will automatically be named 'research_report.pdf'."
    )
    try:
        filename = await asyncio.wait_for(
            loop.run_in_executor(None, input, "Enter the filename: "),
            timeout=20.0,
        )
        filename = filename.strip()
        if filename:
            # TODO: Send the filename_signal to the workflow handle
            # Hint: await handle.signal("filename_signal", FilenameSave(filename=filename))
            print(f"Your file will be saved as {filename}.pdf.")
        else:
            print("No filename entered. Using default: research_report.pdf")
    except TimeoutError:
        print("\n20 seconds have passed. Using default: research_report.pdf")


async def query_research_stats(client: Client, workflow_id: str) -> None:
    """Query the workflow for the character count of the research result."""
    handle = client.get_workflow_handle(workflow_id)

    try:
        # TODO: Pass GenerateReportWorkflow.get_research_stats to the query method
        stats = await handle.query(None)

        print("\n" + "=" * 50)
        # TODO: Print the stats variable in the f-string below
        print(f"Research character count: ")
        print("=" * 50)
    except Exception as exc:
        print(f"Research stats query failed: {exc}")


async def main() -> None:
    client = await Client.connect("localhost:7233")

    print("Welcome to the Research Report Generator!")
    prompt = input("Enter your research topic or question: ").strip()

    if not prompt:
        prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
        print(f"No prompt entered. Using default: {prompt}")

    handle = await client.start_workflow(
        GenerateReportWorkflow,
        GenerateReportInput(prompt=prompt),
        id=f"generate-research-report-workflow-{uuid.uuid4()}",
        task_queue="exercise-03-human-in-the-loop",
    )

    print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")

    signal_task = asyncio.create_task(send_user_decision_signal(client, handle.id))

    try:
        result = await handle.result()
        signal_task.cancel()
        print(f"Result: {result.result}")
    except Exception as exc:
        signal_task.cancel()
        print(f"Workflow failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
