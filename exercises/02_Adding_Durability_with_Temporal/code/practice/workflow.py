# ABOUTME: Temporal Workflow that orchestrates LLM research, image generation, and PDF creation.
# ABOUTME: Demonstrates durable execution — survives worker restarts without losing progress.

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import create_pdf, generate_ai_image, llm_call
    from models import (
        GenerateImageInput,
        GenerateReportInput,
        GenerateReportOutput,
        LLMCallInput,
        PDFGenerationInput,
    )


@workflow.defn
class GenerateReportWorkflow:
    # TODO: Add the @workflow.run decorator to the run method below
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
        research_input = LLMCallInput(prompt=input.prompt)

        research_facts = await workflow.execute_activity(
            llm_call,  # TODO: If this were blank, you would need to specify the llm_call activity here
            research_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info("Research complete!")

        # Extract the subject from the prompt
        subject_prompt = (
            "What is the main topic of this sentence? Respond with only the topic "
            "in a single word or short phrase. No explanation. "
            f"The sentence is: {input.prompt}"
        )
        subject_input = LLMCallInput(prompt=subject_prompt)

        # TODO: Call the llm_call Activity with subject_input and a
        # start_to_close_timeout of 30 seconds
        topic_call = await workflow.execute_activity(
            llm_call,
            subject_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        topic = topic_call["choices"][0]["message"]["content"]

        # Generate an AI image of the topic
        image_input = GenerateImageInput(topic=topic)

        # TODO: Call the generate_ai_image Activity with image_input.
        # Set the start_to_close_timeout to 1 second.
        # (This is intentionally too short — you'll observe retry failures,
        # then come back and fix it to 30 seconds.)
        ai_image = await workflow.execute_activity(
            generate_ai_image,
            image_input,
            start_to_close_timeout=timedelta(seconds=1),
        )

        image_url = ai_image["data"][0]["url"]

        # Create the PDF with research content and image
        pdf_generation_input = PDFGenerationInput(
            content=research_facts["choices"][0]["message"]["content"],
            image_url=image_url,
            filename=topic,
        )

        pdf_filename = await workflow.execute_activity(
            create_pdf,
            pdf_generation_input,
            # TODO: Set your start_to_close_timeout to 10 seconds
            start_to_close_timeout=timedelta(seconds=10),
        )

        return GenerateReportOutput(result=f"Successfully created research report PDF: {pdf_filename}")
