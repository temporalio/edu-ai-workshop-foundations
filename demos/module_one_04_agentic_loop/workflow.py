from datetime import timedelta

from temporalio import workflow
from models import BookingResult, AgentGoal
from tools import AVAILABLE_TOOLS


@workflow.defn
class AgenticWorkflow:
    @workflow.run
    async def run(self, agent_goal: AgentGoal) -> BookingResult:
        llm_model = agent_goal.llm_model or "openai/gpt-4o-mini"
        llm_api_key = agent_goal.llm_api_key
        
        # Track execution context and steps
        context = ""
        steps_taken: list[str] = []
        max_iterations = 10

        workflow.logger.info(f"Starting agentic loop for goal: {agent_goal.description}")

        for iteration in range(max_iterations):
            workflow.logger.info(f"Agentic loop iteration {iteration + 1}")
            
            # Validate the request aligns with agent capabilities (first iteration only)
            if iteration == 0:
                is_valid = await workflow.execute_activity(
                    "agent_validate_prompt",
                    args=[agent_goal, agent_goal.description, llm_model, llm_api_key],
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                if not is_valid:
                    workflow.logger.warning("Validation failed - request outside agent capabilities")
                    return BookingResult(
                        message="Request outside of agent capabilities",
                        steps_taken=["Validation failed - request not compatible with agent"]
                    )

            # AI decides which tool to use and extracts parameters
            decision = await workflow.execute_activity(
                "ai_select_tool_with_params",
                args=[agent_goal.description, AVAILABLE_TOOLS, context, llm_model, llm_api_key],
                start_to_close_timeout=timedelta(seconds=30),
            )

            selected_tool = decision.get("tool", "")
            parameters = decision.get("parameters", {})
            workflow.logger.info(f"AI selected tool: {selected_tool}")

            if selected_tool.upper() == "DONE":
                workflow.logger.info("AI determined goal is complete")
                break

            if selected_tool not in AVAILABLE_TOOLS:
                workflow.logger.error(f"AI selected unknown tool: {selected_tool}")
                context += f"\nError: Unknown tool '{selected_tool}'"
                continue

            workflow.logger.info(f"Executing tool: {selected_tool} with params: {parameters}")

            try:
                result: str = await workflow.execute_activity(
                    selected_tool,
                    args=[parameters],
                    start_to_close_timeout=timedelta(seconds=30),
                )

                # Update context for AI decision-making
                context += f"\n\nExecuted: {selected_tool}\nResult: {result}"
                
                # Track that we completed this tool
                steps_taken.append(selected_tool)

                workflow.logger.info(f"Tool result: {result[:200]}...")

            except Exception as e:
                workflow.logger.error(f"Error executing {selected_tool}: {e}")
                context += f"\nError: {selected_tool} failed - {e}"
                steps_taken.append(f"{selected_tool} (failed)")

        # Prepare final result
        if not steps_taken:
            steps_taken = ["No actions were taken"]

        # Determine success based on whether booking was completed
        success = any("book_flight" in step and "failed" not in step for step in steps_taken)

        message = f"{'Successfully completed' if success else 'Partially completed'}: {agent_goal.description}"

        return BookingResult(
            message=message,
            steps_taken=steps_taken
        )