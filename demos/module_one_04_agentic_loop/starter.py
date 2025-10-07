import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from models import AgentGoal
from temporalio.client import Client
from workflow import AgenticWorkflow
from tools import AVAILABLE_TOOLS

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


async def main() -> None:
    client = await Client.connect("localhost:7233")
    
    goal = input("What are your trip booking details? ").strip()
    if not goal:
        goal = "Book a flight from NYC to London for tomorrow"
        print(f"Using default goal: {goal}")

    agent_goal = AgentGoal(
        agent_name="Travel Booking Assistant",
        tools=list(AVAILABLE_TOOLS.values()),
        description=goal,
        starter_prompt="You are an expert travel agent helping users book their perfect trips.",
        example_conversation_history="User: I need to fly to Paris\nAgent: I'll help you find flights to Paris. What's your departure city?",
        llm_model=os.environ.get("LLM_MODEL", "openai/gpt-4o-mini"),
        llm_api_key=os.environ.get("LLM_API_KEY")
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

if __name__ == "__main__":
    asyncio.run(main())