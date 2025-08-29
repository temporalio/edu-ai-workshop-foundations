from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import create_pdf, llm_call
    from models import (
        GenerateReportInput,
        GenerateReportOutput,
        LLMCallInput,
        PDFGenerationInput,
        UserDecision,
        UserDecisionSignal,
    )

@workflow.defn
class GenerateReportWorkflow:
    def __init__(self) -> None:
        self._current_prompt: str = ""
        self._user_decision: UserDecisionSignal = UserDecisionSignal(
            decision=UserDecision.WAIT
        )  # UserDecision Signal starts with WAIT as the default state
        self._research_result: str | None = None
   
    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        self._user_decision = decision_data


    @workflow.query
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

            # Store the research result for queries
            self._research_result = research_facts["choices"][0]["message"]["content"]

            print("Research complete!")

            print("Waiting for user decision. Send signal with 'keep' to create PDF or 'edit' to modify research.")
            await workflow.wait_condition(lambda: self._user_decision.decision != UserDecision.WAIT)

            user_decision = self._user_decision

            if user_decision.decision == UserDecision.KEEP:
                print("User approved the research. Creating PDF...")
                continue_agent_loop = False
            elif user_decision.decision == UserDecision.EDIT:
                print("User requested research modification.")
                if user_decision.additional_prompt != "":
                    self._current_prompt = (
                        f"{self._current_prompt}\n\nAdditional instructions: {user_decision.additional_prompt}"
                    )
                    print(f"Regenerating research with updated prompt: {self._current_prompt}")
                else:
                    print("No additional instructions provided. Regenerating with original prompt.")
                llm_call_input.prompt = self._current_prompt
                self._user_decision = UserDecisionSignal(decision=UserDecision.WAIT)

        pdf_generation_input = PDFGenerationInput(content=research_facts["choices"][0]["message"]["content"])

        pdf_filename: str = await workflow.execute_activity(
            create_pdf,
            pdf_generation_input,
            start_to_close_timeout=timedelta(seconds=20),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_attempts=3,
                backoff_coefficient=2.0,
            ),
        )

        return GenerateReportOutput(result=f"Successfully created research report PDF: {pdf_filename}")