import asyncio
from datetime import timedelta
import logging

from temporalio import workflow

# sandboxed=False is a Notebook only requirement. You normally don't do this
@workflow.defn(sandboxed=False)
class GenerateReportWorkflow:

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:

        llm_call_input = LLMCallInput(prompt=input.prompt, llm_api_key=LLM_API_KEY, llm_model=LLM_MODEL)

        research_facts = await workflow.execute_activity(
            llm_call,
            llm_call_input,
            start_to_close_timeout=timedelta(seconds=30), # maximum amount of time a single Activity Execution can take.
        )

        workflow.logger.info("Research complete!")

        pdf_generation_input = PDFGenerationInput(content=research_facts["choices"][0]["message"]["content"])

        pdf_filename = await workflow.execute_activity(
            create_pdf_activity,
            pdf_generation_input,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return GenerateReportOutput(result=f"Successfully created research report PDF: {pdf_filename}")