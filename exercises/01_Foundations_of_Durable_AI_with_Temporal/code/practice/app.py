# ABOUTME: Non-durable AI research report generator with LLM calls, image generation, and PDF creation.
# ABOUTME: Demonstrates the fragility of a sequential script — kill the process to lose all progress.

import os
import time
from io import BytesIO

import requests
from dotenv import load_dotenv
from litellm import completion, image_generation
from litellm.types.utils import ModelResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

load_dotenv(override=True)

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")


def llm_call(prompt: str) -> ModelResponse:
    """Send a prompt to the LLM and return the response."""
    return completion(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        messages=[{"content": prompt, "role": "user"}],
    )


def create_pdf(content: str, filename: str = "research_report.pdf", image_url: str | None = None) -> str:
    """Convert text content and an optional image into a PDF document."""
    doc = SimpleDocTemplate(filename, pagesize=letter)

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

    if image_url is not None:
        img_response = requests.get(image_url)
        img_buffer = BytesIO(img_response.content)
        img = RLImage(img_buffer, width=5 * inch, height=5 * inch)
        story.append(img)
        story.append(Spacer(1, 20))

    paragraphs = content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            paragraph = Paragraph(para.strip(), styles["Normal"])
            story.append(paragraph)
            story.append(Spacer(1, 12))

    doc.build(story)
    return filename


def generate_ai_image(subject: str) -> ModelResponse:
    """Generate an AI image of the given subject using DALL-E."""
    # TODO: Create an image prompt that includes the subject.
    # Example: f"A cute, natural image of {subject}."
    image_prompt = ""

    # TODO: Call the image_generation function with the image_prompt,
    # model="dall-e-3", and api_key=LLM_API_KEY.
    # Return the response.
    pass


# Main flow
print("Welcome to the Research Report Generator!")
research_prompt = input("Enter your research topic or question: ").strip()

if not research_prompt:
    research_prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {research_prompt}")

# Step 1: Research with LLM
print("\nStep 1: Getting research from LLM. Please wait...")
result = llm_call(research_prompt)
response_content: str = result["choices"][0]["message"]["content"]
print("Research complete!")

# Step 2: Extract the subject from the prompt
# TODO: Create a subject_prompt that asks the LLM to extract the main topic
# from research_prompt as a single word or short phrase.
# Then call llm_call() with that prompt and extract the topic from the response.
subject_prompt = ""
research_topic = ""

# Step 3: Generate an image of the subject
# TODO: Call the generate_ai_image function with research_topic
# and extract the image URL from the response at ["data"][0]["url"].
print("\nStep 2: Generating AI image. Please wait...")
ai_image_url = None

# Demonstrate fragility: countdown gives you time to kill the process
print("\nNow demonstrating execution fragility:")
print("Press Ctrl+C within the next 15 seconds to simulate a process crash.")
print("Then restart the script to see how you lose all progress...\n")

for countdown in range(15, 0, -1):
    print(f"Continuing in {countdown} seconds... (Press Ctrl+C to kill process)")
    time.sleep(1)

# Step 4: Create PDF with research and image
print("\nStep 3: Creating PDF Document")
pdf_filename = create_pdf(response_content, f"{research_topic}.pdf", ai_image_url)
print(f"SUCCESS! PDF created: {pdf_filename}")
