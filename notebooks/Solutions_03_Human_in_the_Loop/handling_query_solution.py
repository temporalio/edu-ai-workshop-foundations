# Adding a Query into our Workflow code
import asyncio
from datetime import timedelta
import logging

from temporalio import workflow

@workflow.defn(sandboxed=False)
class GenerateReportWorkflow:
    def __init__(self) -> None:
        self._current_prompt: str = ""
        # Instance variable to store the Signal in
        self._user_decision: UserDecisionSignal = UserDecisionSignal(decision=UserDecision.WAIT)
        self._research_result: str = ""

    # Method to handle the Signal
    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        # Update the instance variable with the received Signal data
        self._user_decision = decision_data

    @workflow.query # Query to get the current research result
    def get_research_result(self) -> str | None:
        return self._research_result

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
        self._current_prompt = input.prompt

        llm_call_input = LLMCallInput(
            prompt=self._current_prompt,
            llm_api_key=input.llm_api_key,
            llm_model=input.llm_research_model,
        )

        continue_agent_loop = True

        while continue_agent_loop:
            research_facts = await workflow.execute_activity(
                llm_call,
                llm_call_input,
                start_to_close_timeout=timedelta(seconds=30),
            )

            self._research_result = research_facts["choices"][0]["message"]["content"] # Setting result of research with LLM result

            # Waiting for Signal with user decision
            await workflow.wait_condition(lambda: self._user_decision.decision != UserDecision.WAIT)

            if self._user_decision.decision == UserDecision.KEEP:
                workflow.logger.info("User approved the research. Creating PDF...")
                continue_agent_loop = False
            elif self._user_decision.decision == UserDecision.EDIT:
                workflow.logger.info("User requested research modification.")
                if self._user_decision.additional_prompt != "":
                    self._current_prompt = (
                        f"{self._current_prompt}\n\nAdditional instructions: {self._user_decision.additional_prompt}"
                    )
                    workflow.logger.info(f"Regenerating research with updated prompt: {self._current_prompt}")
                else:
                    workflow.logger.info("No additional instructions provided. Regenerating with original prompt.")
                llm_call_input.prompt = self._current_prompt

                # Set the decision back to WAIT for the next loop
                self._user_decision = UserDecisionSignal(decision=UserDecision.WAIT)

        pdf_generation_input = PDFGenerationInput(content=research_facts["choices"][0]["message"]["content"])

        pdf_filename: str = await workflow.execute_activity(
            create_pdf,
            pdf_generation_input,
            start_to_close_timeout=timedelta(seconds=20),
        )

        return GenerateReportOutput(result=f"Successfully created research report PDF: {pdf_filename}")