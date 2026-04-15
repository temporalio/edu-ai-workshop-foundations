# ABOUTME: Temporal Workflow with signal and query handlers for interactive human-in-the-loop control.
# ABOUTME: Supports keep/edit decisions, filename signals with timeout, and character count queries.

import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import create_pdf, generate_ai_image, llm_call
    from models import (
        FilenameSave,
        GenerateImageInput,
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
        self._user_decision: UserDecisionSignal = UserDecisionSignal(decision=UserDecision.WAIT)
        self._research_result: str | None = None
        # TODO: Set _filename to a string with default value "research_report"
        self._filename: str = ""
        # TODO: Add a _character_count attribute as an int, defaulting to 0

    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        self._user_decision = decision_data

    # TODO: Add the @workflow.signal decorator to the method below
    async def filename_signal(self, input: FilenameSave) -> None:
        if input.filename.strip():
            self._filename = input.filename

    @workflow.query
    def get_research_result(self) -> str | None:
        return self._research_result

    # TODO: Add a @workflow.query handler called get_research_stats
    # that returns self._character_count

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
        self._current_prompt = input.prompt

        llm_call_input = LLMCallInput(prompt=self._current_prompt)

        continue_user_input_loop = True

        while continue_user_input_loop:
            research_facts = await workflow.execute_activity(
                llm_call,
                llm_call_input,
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Store the research result for queries
            self._research_result = research_facts["choices"][0]["message"]["content"]
            # TODO: Set self._character_count to the length of the research content
            # Hint: len(research_facts["choices"][0]["message"]["content"])

            workflow.logger.info("Research complete!")
            workflow.logger.info("Waiting for user decision.")

            await workflow.wait_condition(lambda: self._user_decision.decision != UserDecision.WAIT)

            if self._user_decision.decision == UserDecision.KEEP:
                workflow.logger.info("User approved the research. Creating PDF...")
                continue_user_input_loop = False
            elif self._user_decision.decision == UserDecision.EDIT:
                workflow.logger.info("User requested research modification.")
                if self._user_decision.additional_prompt != "":
                    self._current_prompt = (
                        f"{self._current_prompt}\n\nAdditional instructions: "
                        f"{self._user_decision.additional_prompt}"
                    )
                    workflow.logger.info(f"Regenerating research with updated prompt: {self._current_prompt}")
                else:
                    workflow.logger.info("No additional instructions provided. Regenerating with original prompt.")
                llm_call_input.prompt = self._current_prompt
                self._user_decision = UserDecisionSignal(decision=UserDecision.WAIT)

        # Extract the subject for image generation
        subject_prompt = (
            "What is the main topic of this sentence? Respond with only the topic "
            "in a single word or short phrase if multiple topics are detected. "
            "This response will be used for generating an AI image. No explanation. "
            f"The sentence is: {self._current_prompt}"
        )
        subject_input = LLMCallInput(prompt=subject_prompt)

        topic_call = await workflow.execute_activity(
            llm_call,
            subject_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        topic = topic_call["choices"][0]["message"]["content"]

        # Generate an AI image of the topic
        image_input = GenerateImageInput(topic=topic)

        # TODO: Call the generate_ai_image Activity with image_input
        # and a start_to_close_timeout of 30 seconds
        ai_image = await workflow.execute_activity(
            generate_ai_image,
            image_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        image_url = ai_image["data"][0]["url"]

        # Wait for filename signal with a 20-second timeout
        try:
            await workflow.wait_condition(
                # TODO: Set the condition — self._filename should not equal "research_report"
                lambda: False,
                # TODO: Set the timeout to 20 seconds using timedelta(seconds=20)
                timeout=timedelta(seconds=0),
            )
        except asyncio.TimeoutError:
            workflow.logger.info(
                "20 seconds have passed. The file will automatically be named 'research_report.pdf'."
            )

        # Create the PDF with research content and image
        pdf_generation_input = PDFGenerationInput(
            content=research_facts["choices"][0]["message"]["content"],
            image_url=image_url,
            filename=self._filename,
        )

        pdf_filename = await workflow.execute_activity(
            create_pdf,
            pdf_generation_input,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_attempts=3,
                backoff_coefficient=2.0,
            ),
        )

        return GenerateReportOutput(result=f"Successfully created research report PDF: {pdf_filename}.pdf")
