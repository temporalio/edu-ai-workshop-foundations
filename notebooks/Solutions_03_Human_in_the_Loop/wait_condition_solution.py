from temporalio import workflow

@workflow.defn(sandboxed=False)
class GenerateReportWorkflow:

    def __init__(self) -> None:
        self._current_prompt: str = ""
        # Instance variable to store the Signal in
        self._user_decision: UserDecisionSignal = UserDecisionSignal(decision=UserDecision.WAIT) # UserDecision Signal starts with WAIT as the default state

    # Method to handle the Signal
    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        # Update the instance variable with the received Signal data
        self._user_decision = decision_data

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

            self._research_result = research_facts["choices"][0]["message"]["content"]

            # Waiting for Signal with user decision
            await workflow.wait_condition(lambda: self._user_decision.decision != UserDecision.WAIT)

            # rest of code here