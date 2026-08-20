"""
Learner Skill State and Multi-Dimensional Mastery Vector

Section 15, 18, 24:
Mastery is NOT a boolean (learned=true). It is a multidimensional vector:
- recognition
- listening
- production
- pronunciation
- composition
- pragmatics
- automaticity latency (median_latency_ms)
- memory stability and retrievability
"""

from __future__ import annotations
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class MemoryState(BaseModel):
    stability_days: float = Field(default=1.0, ge=0.01)
    retrievability: float = Field(default=1.0, ge=0.0, le=1.0)
    last_reviewed_at: Optional[str] = None


class SkillStatistics(BaseModel):
    exposures: int = 0
    retrievals: int = 0
    successes: int = 0
    failures: int = 0


class MasteryVector(BaseModel):
    recognition: float = Field(default=0.0, ge=0.0, le=1.0)
    listening: float = Field(default=0.0, ge=0.0, le=1.0)
    production: float = Field(default=0.0, ge=0.0, le=1.0)
    pronunciation: float = Field(default=0.0, ge=0.0, le=1.0)
    composition: float = Field(default=0.0, ge=0.0, le=1.0)
    pragmatics: float = Field(default=0.0, ge=0.0, le=1.0)
    
    @property
    def overall_mastery(self) -> float:
        return (
            self.recognition * 0.25
            + self.listening * 0.15
            + self.production * 0.35
            + self.composition * 0.15
            + self.pragmatics * 0.10
        )


class LearnerSkillState(BaseModel):
    learner_id: str
    skill_id: str  # e.g. "JP.CONDITION.TARA" or "CORE.CONDITION"
    
    # Mastery dimensions
    mastery: MasteryVector = Field(default_factory=MasteryVector)
    
    # Latency / Automaticity (Section 18)
    median_latency_ms: float = 3500.0  # Initial baseline latency
    
    # Memory State (Section 17)
    memory: MemoryState = Field(default_factory=MemoryState)
    
    # Interaction Statistics
    statistics: SkillStatistics = Field(default_factory=SkillStatistics)
    
    def is_fluent(self, threshold_ms: float = 1800.0, min_production: float = 0.8) -> bool:
        """Fluent requires high production mastery AND low latency (automaticity)."""
        return self.mastery.production >= min_production and self.median_latency_ms <= threshold_ms

    def record_latency(self, latency_ms: float):
        # Exponential moving average for median latency estimation
        alpha = 0.3
        self.median_latency_ms = (1 - alpha) * self.median_latency_ms + alpha * latency_ms


class LearnerProfile(BaseModel):
    learner_id: str = "user_001"
    name: str = "Learner"
    target_language: str = "ja"
    skills: Dict[str, LearnerSkillState] = Field(default_factory=dict)

    def get_or_create_skill_state(self, skill_id: str) -> LearnerSkillState:
        if skill_id not in self.skills:
            self.skills[skill_id] = LearnerSkillState(learner_id=self.learner_id, skill_id=skill_id)
        return self.skills[skill_id]
