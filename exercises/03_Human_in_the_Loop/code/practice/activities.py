# ABOUTME: Temporal Activity definitions for LLM calls, image generation, and PDF creation.
# ABOUTME: Activities wrap non-deterministic operations so Temporal can retry and track them.

import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from litellm import completion, image_generation
from litellm.types.utils import ModelResponse
from models import GenerateImageInput, LLMCallInput, PDFGenerationInput
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from temporalio import activity

load_dotenv(override=True)

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")


@activity.defn
def llm_call(input: LLMCallInput) -> ModelResponse:
    """Send a prompt to the LLM and return the response."""
    return completion(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        messages=[{"content": input.prompt, "role": "user"}],
    )


@activity.defn
def generate_ai_image(input: GenerateImageInput) -> ModelResponse:
    """Generate an AI image of the given topic using DALL-E."""
    image_prompt = f"A cute, natural image of {input.topic}."

    response = image_generation(
        prompt=image_prompt,
        api_key=LLM_API_KEY,
    )

    return response


@activity.defn
def create_pdf(input: PDFGenerationInput) -> str:
    """Convert text content and an optional image into a PDF document."""
    doc = SimpleDocTemplate(f"{input.filename}.pdf", pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
    )

    story = []
    title = Paragraph("Research Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))

    if input.image_url is not None:
        img_response = requests.get(input.image_url)
        img_buffer = BytesIO(img_response.content)
        img = RLImage(img_buffer, width=5 * inch, height=5 * inch)
        story.append(img)
        story.append(Spacer(1, 20))

    paragraphs = input.content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            paragraph = Paragraph(para.strip(), styles["Normal"])
            story.append(paragraph)
            story.append(Spacer(1, 12))

    doc.build(story)
    return input.filename
