import os
import sys

from temporalio import activity
from temporalio.exceptions import ApplicationError

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import OPENAI_API_KEY
from litellm import completion, image_generation

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import requests
from io import BytesIO

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class GenerateReportActivities:

    @activity.defn
    async def perform_research(self, prompt: str, model: str = "openai/gpt-4o") -> str:
        response = completion(
            model=model,
            messages=[{"content": prompt, "role": "user"}]
        )
        
        research_response = response["choices"][0]["message"]["content"]
        return research_response

    @activity.defn
    async def create_pdf_activity(self, content: str, filename: str = "research_pdf.pdf") -> str:
        attempt = activity.info().attempt
        
        # Fail the first 2 attempts to demonstrate retries
        if attempt <= 2:
            raise ApplicationError(f"PDF creation failed - demonstrating Temporal retries!")
        
        print("Creating PDF document...")
        
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
        
        print(f"SUCCESS! PDF created: {filename}")
        return filename

    @activity.defn
    async def create_pdf_with_image(self, prompt: str, response_content: str) -> str:
        print("\nPART 3: Extracting subject from prompt...")
        subject_prompt = f"""What is the main topic or thing being discussed in this sentence: "{prompt}" """
        subject_response = completion(
            model="openai/gpt-4o",
            messages=[{"content": subject_prompt, "role": "user"}]
        )
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
            
            return pdf_with_image_filename
            
        except Exception as img_error:
            print(f"Error generating image or creating PDF with image: {img_error}")
            raise ApplicationError(f"Failed to generate image or create PDF: {str(img_error)} test")