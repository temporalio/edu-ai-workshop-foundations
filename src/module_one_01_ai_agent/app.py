import os
import time

from dotenv import load_dotenv
from litellm import CustomStreamWrapper, completion
from litellm.types.utils import ModelResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

load_dotenv(override=True)

# Get LLM_API_KEY environment variable
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", None)


def llm_call(prompt: str, llm_api_key: str, llm_model: str) -> ModelResponse | CustomStreamWrapper:  # type: ignore[no-any-unimported]
    return completion(
        model=llm_model,
        api_key=llm_api_key,
        messages=[{"content": prompt, "role": "user"}],
    )


def create_pdf(content: str, filename: str = "research_report.pdf") -> str:
    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
    )

    story: list[Flowable] = []
    title = Paragraph("Research Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))

    paragraphs = content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.strip(), styles["Normal"])
            story.append(p)
            story.append(Spacer(1, 12))

    doc.build(story)
    return filename


print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ").strip()

if not prompt:
    prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {prompt}")

print("\nPART 1: Getting research report from OpenAI. Please wait...")

result = llm_call(prompt, LLM_API_KEY or "", LLM_MODEL)

response_content: str = result["choices"][0]["message"]["content"]

print("Research complete!")

# print("\nNow demonstrating normal execution fragility:")
# print("Press Ctrl+C within the next 15 seconds to simulate a process crash.")
# print("Then restart the script to see how you lose all progress...")

# Long pause to allow killing the process
for i in range(15, 0, -1):
    print(f"Continuing in {i} seconds... (Press Ctrl+C to kill process)")
    time.sleep(1)


print("\nPART 2: Creating PDF Document")

pdf_filename = create_pdf(response_content, "research_report.pdf")
