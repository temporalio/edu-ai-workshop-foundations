from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

@activity.defn
def create_pdf_activity(input: PDFGenerationInput) -> str:
    print("Creating PDF document...")

    doc = SimpleDocTemplate(input.filename, pagesize=letter)
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
    paragraphs = input.content.split('\n\n')
    for para in paragraphs:
        if para.strip():
          p = Paragraph(para.strip(), styles['Normal'])
          story.append(p)
          story.append(Spacer(1, 12))

    doc.build(story)

    print(f"SUCCESS! PDF created: {input.filename}")
    return input.filename