"""
Learning Event Schema and Event Store

Section 16 & Section 41.4:
All learning results MUST form structured LearningEvents.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PromptTarget(BaseModel):
    text: str
    target_skills: List[str] = Field(default_factory=list)


class ResponseObservation(BaseModel):
    text: str
    latency_ms: float = 0.0


class PerformanceObservations(BaseModel):
    understanding: float = Field(default=0.0, ge=0.0, le=1.0)
    grammar: float = Field(default=0.0, ge=0.0, le=1.0)
    naturalness: float = Field(default=0.0, ge=0.0, le=1.0)
    pragmatics: float = Field(default=0.0, ge=0.0, le=1.0)
    pronunciation: Optional[float] = None


class SkillObservation(BaseModel):
    skill_id: str
    dimension: str  # recognition, production, listening, pragmatics
    success: bool
    score: float = 1.0
    notes: Optional[str] = None


class LearningEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    learner_id: str
    scenario: str
    prompt: PromptTarget
    response: ResponseObservation
    observations: PerformanceObservations
    skills: List[SkillObservation] = Field(default_factory=list)
    raw_ir: Optional[Dict[str, Any]] = None


class LearningEventStore:
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path
        self._events: List[LearningEvent] = []

    def record(self, event: LearningEvent):
        self._events.append(event)
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")

    def get_events_for_learner(self, learner_id: str) -> List[LearningEvent]:
        return [e for e in self._events if e.learner_id == learner_id]

    def get_all_events(self) -> List[LearningEvent]:
        return list(self._events)
