"""
Language Adapter Interface Definition

Section 13:
Every Language Adapter must provide:
- parse(text, context) -> CommunicationIR
- realize(ir, context) -> str
- evaluate_naturalness(text, ir, context) -> Evaluation
- get_realizations(concept, context) -> list[Realization]
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.ir_schema import CommunicationIR, ConversationContext


class Realization(BaseModel):
    surface: str
    pattern: Optional[str] = None
    frequency: float = 0.8
    formality: str = "neutral"
    politeness: str = "neutral"
    notes: Optional[str] = None


class Evaluation(BaseModel):
    is_valid: bool = True
    naturalness_score: float = Field(default=0.9, ge=0.0, le=1.0)
    grammar_score: float = Field(default=0.9, ge=0.0, le=1.0)
    pragmatic_score: float = Field(default=0.9, ge=0.0, le=1.0)
    detected_skills: List[str] = Field(default_factory=list)
    feedback: List[str] = Field(default_factory=list)


class LanguageAdapter(ABC):
    @property
    @abstractmethod
    def language_code(self) -> str:
        """Language identifier e.g. 'ja', 'en', 'zh'."""
        pass

    @abstractmethod
    def parse(self, text: str, context: Optional[ConversationContext] = None) -> CommunicationIR:
        """Parse natural language text into Universal Communication IR."""
        pass

    @abstractmethod
    def realize(self, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> str:
        """Realize Universal Communication IR into target natural language text."""
        pass

    @abstractmethod
    def evaluate_naturalness(self, text: str, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> Evaluation:
        """Evaluate naturalness, grammatical correctness, and pragmatic alignment of an utterance."""
        pass

    @abstractmethod
    def get_realizations(self, concept: str, context: Optional[ConversationContext] = None) -> List[Realization]:
        """Get all surface realizations for a given concept in this language."""
        pass
