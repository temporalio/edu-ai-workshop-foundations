# ABOUTME: Data models for the human-in-the-loop research report generator.
# ABOUTME: Includes signal/query models for interactive workflow control.

from dataclasses import dataclass
from enum import StrEnum


class UserDecision(StrEnum):
    KEEP = "KEEP"
    EDIT = "EDIT"
    WAIT = "WAIT"


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
    llm_image_model: str = "dall-e-3"


@dataclass
class GenerateReportOutput:
    result: str


@dataclass
class GenerateImageInput:
    topic: str
    llm_model: str = "dall-e-3"


@dataclass
class UserDecisionSignal:
    decision: UserDecision
    additional_prompt: str = ""


@dataclass
class FilenameSave:
    filename: str
