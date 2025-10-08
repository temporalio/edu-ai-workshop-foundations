from temporalio import workflow
from datetime import timedelta
import json

# sandboxed=False is a Notebook only requirement. You normally don't do this
@workflow.defn(sandboxed=False)
class ToolCallingWorkflow:
    @workflow.run
    async def run(self, input: str) -> str:
        input_list = [{"role": "user", "content": input}]
        
        # Initial LLM call with system instructions and tools
        system_instructions = "if no tools seem to be needed, respond in haikus."
        result = await workflow.execute_activity(
            create,
            OpenAIResponsesRequest(
                model="gpt-4o-mini",
                instructions=system_instructions,
                input=input_list,
                tools=[get_weather_alerts.WEATHER_ALERTS_TOOL_OAI],
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Process the LLM response
        item = result.output[0]
        
        # if the result is a tool call, call the tool
        if item.type == "function_call":
            if item.name == "get_weather_alerts":

                # serialize the output, which is an OpenAI object
                input_list += [
                    i.model_dump() if hasattr(i, "model_dump") else i
                    for i in result.output
                ]
                
                result = await workflow.execute_activity(
                    get_weather_alerts.get_weather_alerts,
                    get_weather_alerts.GetWeatherAlertsRequest(state=json.loads(item.arguments)["state"]),
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                # Add tool call result to input list
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result
                })
                
                result = await workflow.execute_activity(
                    create,
                    OpenAIResponsesRequest(
                        model="gpt-4o-mini",
                        instructions="return the tool call result in a readable format",
                        input=input_list,
                        tools=[]
                    ),
                    start_to_close_timeout=timedelta(seconds=30),
                )
        
        result = result.output_text
        return result