from dataclasses import dataclass
from enum import StrEnum

class UserDecision(StrEnum):
    KEEP = "KEEP"
    EDIT = "EDIT"
    WAIT = "WAIT"
    
@dataclass
class UserDecisionSignal: # A data structure to send user decisions via Temporal Signals
    decision: UserDecision
    additional_prompt: str = ""