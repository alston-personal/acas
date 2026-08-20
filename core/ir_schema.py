"""
Universal Communication IR Core Schema v0.1

Provides the unified, language-independent representation for all utterances.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from core.primitives import (
    IntentPrimitive,
    FormalityLevel,
    PolitenessLevel,
    DirectnessLevel,
)


class IntentNode(BaseModel):
    type: IntentPrimitive
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    subtype: Optional[str] = None


class Pragmatics(BaseModel):
    formality: FormalityLevel = FormalityLevel.NEUTRAL
    politeness: PolitenessLevel = PolitenessLevel.NEUTRAL
    directness: DirectnessLevel = DirectnessLevel.DIRECT
    social_distance: Optional[str] = "unknown"
    emotion: Optional[str] = None
    emphasis: Optional[str] = None
    certainty_level: Optional[float] = None
    speech_register: str = Field(default="casual", alias="register")


class ConversationContext(BaseModel):
    speaker: str = "user"
    listener: str = "assistant"
    conversation_id: Optional[str] = None
    scenario_id: Optional[str] = None
    topic: Optional[str] = None
    turn_index: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArgumentEntity(BaseModel):
    type: str = "ENTITY"
    ref: Optional[str] = None
    concept: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class TimeRelation(BaseModel):
    type: str = "TIME"
    relation: str = "PRESENT"
    value: Optional[str] = None


class ContentNode(BaseModel):
    type: str
    predicate: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    time: Optional[Union[TimeRelation, Dict[str, Any]]] = None
    
    scope: Optional[Union[ContentNode, Dict[str, Any]]] = None
    cause: Optional[Union[ContentNode, Dict[str, Any]]] = None
    effect: Optional[Union[ContentNode, Dict[str, Any]]] = None
    condition: Optional[Union[ContentNode, Dict[str, Any]]] = None
    consequence: Optional[Union[ContentNode, Dict[str, Any]]] = None
    content: Optional[Union[ContentNode, Dict[str, Any]]] = None
    holder: Optional[Dict[str, Any]] = None
    probability: Optional[str] = None
    contrast_a: Optional[Union[ContentNode, Dict[str, Any]]] = None
    contrast_b: Optional[Union[ContentNode, Dict[str, Any]]] = None
    degree: Optional[str] = None
    target: Optional[Any] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class CommunicationIR(BaseModel):
    ir_version: str = "0.1"
    type: str = "utterance"
    intent: IntentNode
    content: Union[ContentNode, Dict[str, Any]]
    pragmatics: Pragmatics = Field(default_factory=Pragmatics)
    context: ConversationContext = Field(default_factory=ConversationContext)

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CommunicationIR:
        return cls.model_validate(data)
