import os
import sys
import time
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import OPENAI_API_KEY
from litellm import completion, ModelResponse, image_generation

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import requests
from io import BytesIO

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def llm_call(prompt: str, model: str = "openai/gpt-4o") -> ModelResponse:
    response = completion(
        model=model,
        messages=[{"content": prompt, "role": "user"}]
    )
    return response

def create_pdf(content: str, filename: str = "research_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    story = []
    title = Paragraph("Research Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.strip(), styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))
    
    doc.build(story)
    return filename

print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ").strip()

if len(sys.argv) > 1:
    prompt = sys.argv[1]
elif not prompt:
    prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {prompt}")

print("\nPART 1: Getting research report from OpenAI. Please wait...")

try:
    result = llm_call(prompt)
    
    response_content = result["choices"][0]["message"]["content"]
    
    print("Research complete!")
     
    # Long pause to allow killing the process
    for i in range(15, 0, -1):
        print(f"Continuing in {i} seconds... (Press Ctrl+C to kill process)")
        time.sleep(1)
    
except Exception as e:
    print(f"Error: {e}")

print("\nPART 2: Creating PDF Document")

try:
    if 'response_content' in locals() and response_content:
        print("Now generating your PDF with your research...")
        
        pdf_filename = create_pdf(response_content, "research_report.pdf")
        print(f"SUCCESS! PDF created: {pdf_filename}")
        
        print("\nPART 3: Extracting subject from prompt...")
        subject_prompt = f"""What is the subject of this sentence: "{prompt}" """
        subject_response = llm_call(subject_prompt)
        subject = subject_response["choices"][0]["message"]["content"].strip().lower()
        
        print("\nPART 4: Generating image...")
        try:
            image_prompt = f"A colorful, educational illustration of {subject} suitable for a research report"
            print(f"Image prompt: {image_prompt}")
            
            response = image_generation(
                prompt=image_prompt,
                model="dall-e-3",
                api_key=OPENAI_API_KEY
            )
            image_url = response["data"][0]["url"]
            print(f"Image generated successfully!")
            
            print("\nPART 5: Creating PDF with image...")
            img_response = requests.get(image_url)
            img_buffer = BytesIO(img_response.content)
            
            # Create filename with subject
            safe_subject = subject.replace(" ", "_").replace("/", "_").replace("\\", "_")[:30]  # Clean filename
            pdf_with_image_filename = f"{safe_subject}_research_report.pdf"
            
            # Create new PDF with image
            doc = SimpleDocTemplate(pdf_with_image_filename, pagesize=letter)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            
            story = []
            
            title = Paragraph(f"Research Report: {subject}", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            img = RLImage(img_buffer, width=5*inch, height=5*inch)
            story.append(img)
            story.append(Spacer(1, 20))
            
            paragraphs = response_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    p = Paragraph(para.strip(), styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 12))
            
            doc.build(story)
            print(f"SUCCESS! PDF with image created: {pdf_with_image_filename}")
            
        except Exception as img_error:
            print(f"Error generating image or creating PDF with image: {img_error}")
    else:
        print("No research content available to create PDF.")
        
except Exception as e:
    print(f"Error: {e}")