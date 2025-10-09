from temporalio import workflow
from datetime import timedelta

# sandboxed=False is a Notebook only requirement. You normally don't do this
@workflow.defn(sandboxed=False)
class GenerateReportWorkflow:
    def __init__(self) -> None:
        self._current_prompt: str = ""

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
        self._current_prompt = input.prompt

    llm_call_input = LLMCallInput(
        prompt=self._current_prompt,
        llm_api_key=input.llm_api_key,
        llm_model=input.llm_research_model,
    )
    
    # Continue looping until the user approves the research
    continue_agent_loop = True

    # Execute the LLM call to generate research based on the current prompt
    while continue_agent_loop:
        research_facts = await workflow.execute_activity(
            llm_call,
            llm_call_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # User approved the research - exit the loop and proceed to PDF generation
        if self._user_decision.decision == UserDecision.KEEP:
            workflow.logger.info("User approved the research. Creating PDF...")
            continue_agent_loop = False
        # User wants to edit the research - update the prompt and loop again
        elif self._user_decision.decision == UserDecision.EDIT:
            workflow.logger.info("User requested research modification.")
            if self._user_decision.additional_prompt != "":
                # Append the user's additional instructions to the existing prompt
                self._current_prompt = (
                    f"{self._current_prompt}\n\nAdditional instructions: {self._user_decision.additional_prompt}"
                )
            else:
                workflow.logger.info("No additional instructions provided. Regenerating with original prompt.")
            # Update the Activity input with the modified prompt for the next iteration
            llm_call_input.prompt = self._current_prompt