from dataclasses import dataclass
from enum import StrEnum


class UserDecision(StrEnum):
    KEEP = "KEEP"
    EDIT = "EDIT"
    WAIT = "WAIT"


@dataclass
class LLMCallInput:
    prompt: str
    llm_api_key: str
    llm_model: str


@dataclass
class PDFGenerationInput:
    content: str
    filename: str = "research_pdf.pdf"


@dataclass
class GenerateReportInput:
    prompt: str
    llm_api_key: str
    llm_research_model: str = "openai/gpt-4o"
    llm_image_model: str = "dall-e-3"


@dataclass
class GenerateReportOutput:
    result: str


@dataclass
class UserDecisionSignal:
    decision: UserDecision
    additional_prompt: str = ""
