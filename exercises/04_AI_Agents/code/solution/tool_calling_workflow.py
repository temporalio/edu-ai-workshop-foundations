# ABOUTME: Temporal Workflow that demonstrates single tool-calling with the OpenAI Responses API.
# ABOUTME: Calls the LLM with a weather alerts tool, executes it if chosen, and returns a formatted result.

import json
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import create, get_weather_alerts
    from models import GetWeatherAlertsRequest, OpenAIResponsesRequest
    from tools import WEATHER_ALERTS_TOOL_OAI


@workflow.defn
class ToolCallingWorkflow:
    @workflow.run
    async def run(self, input: str) -> str:
        input_list = [{"role": "user", "content": input}]

        system_instructions = "if no tools seem to be needed, respond in haikus."

        # Initial LLM call with the weather alerts tool
        result = await workflow.execute_activity(
            create,
            OpenAIResponsesRequest(
                model="gpt-4o-mini",
                instructions=system_instructions,
                input=input_list,
                tools=[WEATHER_ALERTS_TOOL_OAI],
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Process the LLM response
        item = result.output[0]

        # If the LLM chose to call the weather tool, execute it
        if item.type == "function_call" and item.name == "get_weather_alerts":
            # Serialize the LLM output for context
            input_list += [
                i.model_dump() if hasattr(i, "model_dump") else i
                for i in result.output
            ]

            tool_result = await workflow.execute_activity(
                get_weather_alerts,
                GetWeatherAlertsRequest(state=json.loads(item.arguments)["state"]),
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Add tool result to context
            input_list.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": tool_result,
            })

            # Final LLM call to format the result
            result = await workflow.execute_activity(
                create,
                OpenAIResponsesRequest(
                    model="gpt-4o-mini",
                    instructions="return the tool call result in a readable format",
                    input=input_list,
                    tools=[],
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )

        return result.output_text
