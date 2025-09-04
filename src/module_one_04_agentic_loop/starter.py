import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models import AgentGoal
from temporalio.client import Client
from workflow import AgenticWorkflow
from tools import AVAILABLE_TOOLS


async def main() -> None:
    client = await Client.connect("localhost:7233")
    
    goal = input("What are your trip booking details? ").strip()
    if not goal:
        goal = "Book a flight from NYC to London for tomorrow"
        print(f"Using default goal: {goal}")

    # Create the AgentGoal
    agent_goal = AgentGoal(
        agent_name="Travel Booking Assistant",
        tools=list(AVAILABLE_TOOLS.values()),
        description=goal,
        starter_prompt="You are an expert travel agent helping users book their perfect trips.",
        example_conversation_history="User: I need to fly to Paris\nAgent: I'll help you find flights to Paris. What's your departure city?"
    )

    print("Starting agentic workflow...")

    handle = await client.start_workflow(
        AgenticWorkflow.run,
        agent_goal,
        id="agentic-workflow",
        task_queue="agentic-queue",
    )

    result = await handle.result()

    print(result.message)
    print("\nSteps taken by AI agent:")
    for i, step in enumerate(result.steps_taken, 1):
        print(f"   {i}. {step}")

if __name__ == "__main__":
    asyncio.run(main())