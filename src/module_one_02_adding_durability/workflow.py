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
    )


@workflow.defn
class GenerateReportWorkflow:
    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
        llm_call_input = LLMCallInput(
            prompt=input.prompt,
            llm_api_key=input.llm_api_key,
            llm_model=input.llm_research_model,
        )

        research_facts = await workflow.execute_activity(
            llm_call,
            llm_call_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        print("Research complete!")

        # Uncomment to add delay
        # await workflow.sleep(timedelta(seconds=20))

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
