# ABOUTME: Data models for the durable research report generator workflow.
# ABOUTME: Defines input/output types for activities and the workflow.

from dataclasses import dataclass


@dataclass
class LLMCallInput:
    prompt: str


@dataclass
class PDFGenerationInput:
    content: str
    image_url: str | None = None
    filename: str = "research_pdf"


@dataclass
class GenerateReportInput:
    prompt: str


@dataclass
class GenerateReportOutput:
    result: str


@dataclass
class GenerateImageInput:
    topic: str
    llm_model: str = "dall-e-3"
