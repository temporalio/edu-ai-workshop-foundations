# ABOUTME: Temporal Workflow implementing a multi-turn agentic loop with dynamic tool dispatch.
# ABOUTME: The LLM decides which tools to call in a loop until the task is complete.

import json
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import create
    from models import HELPFUL_AGENT_SYSTEM_INSTRUCTIONS, OpenAIResponsesRequest
    from tools import get_tools


@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, input: str) -> str:
        input_list = [{"type": "message", "role": "user", "content": input}]

        while True:
            workflow.logger.info("=" * 80)

            # Consult the LLM with all available tools
            result = await workflow.execute_activity(
                create,
                OpenAIResponsesRequest(
                    model="gpt-4o-mini",
                    instructions=HELPFUL_AGENT_SYSTEM_INSTRUCTIONS,
                    input=input_list,
                    tools=get_tools(),
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )

            item = result.output[0]

            if item.type == "function_call":
                result = await self._handle_function_call(item, result, input_list)

                # Add the tool call result to the input list for context
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result,
                })
            else:
                workflow.logger.info(f"No tools chosen, responding with a message: {result.output_text}")
                return result.output_text

    async def _handle_function_call(self, item, result, input_list):
        """Execute a tool call chosen by the LLM using dynamic activities."""
        # Serialize the LLM output — the decision to call a tool
        serialized_item = result.output[0]
        input_list += [
            serialized_item.model_dump() if hasattr(serialized_item, "model_dump") else serialized_item
        ]

        # Parse the tool arguments
        args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments

        # Execute dynamic activity with the tool name chosen by the LLM
        tool_result = await workflow.execute_activity(
            item.name,
            args,
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(f"Made a tool call to {item.name}")
        return tool_result
