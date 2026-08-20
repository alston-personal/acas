"""
Learner Profile and Multidimensional Mastery Model with Adaptive Difficulty Tracking.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from core.memory_model import AdaptivePowerLawMemoryModel, MemoryState


class MasteryVector(BaseModel):
    recognition: float = Field(default=0.0, ge=0.0, le=1.0)
    listening: float = Field(default=0.0, ge=0.0, le=1.0)
    production: float = Field(default=0.0, ge=0.0, le=1.0)
    pronunciation: float = Field(default=0.0, ge=0.0, le=1.0)
    composition: float = Field(default=0.0, ge=0.0, le=1.0)
    pragmatics: float = Field(default=0.0, ge=0.0, le=1.0)

    @property
    def overall_mastery(self) -> float:
        weights = [0.20, 0.15, 0.25, 0.10, 0.15, 0.15]
        values = [
            self.recognition,
            self.listening,
            self.production,
            self.pronunciation,
            self.composition,
            self.pragmatics,
        ]
        return sum(w * v for w, v in zip(weights, values))


class SkillStatistics(BaseModel):
    exposure_count: int = 0
    success_count: int = 0
    consecutive_correct: int = 0
    consecutive_incorrect: int = 0
    last_practiced_at: float = 0.0


class LearnerSkillState(BaseModel):
    skill_id: str
    mastery: MasteryVector = Field(default_factory=MasteryVector)
    memory: MemoryState = Field(default_factory=MemoryState)
    median_latency_ms: float = 4000.0
    latencies: List[float] = Field(default_factory=list)
    statistics: SkillStatistics = Field(default_factory=SkillStatistics)

    def is_fluent(self, latency_threshold_ms: float = 1800.0) -> bool:
        return self.mastery.overall_mastery >= 0.85 and self.median_latency_ms <= latency_threshold_ms

    def record_performance(self, success: bool, latency_ms: float, timestamp: float, weights: Optional[Dict[str, float]] = None):
        self.statistics.exposure_count += 1
        if success:
            self.statistics.success_count += 1
            self.statistics.consecutive_correct += 1
            self.statistics.consecutive_incorrect = 0
            delta = 0.15
        else:
            self.statistics.consecutive_correct = 0
            self.statistics.consecutive_incorrect += 1
            delta = -0.08

        w = weights or {"production": 0.5, "recognition": 0.3, "composition": 0.2}
        self.mastery.production = max(0.0, min(1.0, self.mastery.production + delta * w.get("production", 0.4)))
        self.mastery.recognition = max(0.0, min(1.0, self.mastery.recognition + (delta * 1.2 if success else delta * 0.5)))
        self.mastery.composition = max(0.0, min(1.0, self.mastery.composition + delta * w.get("composition", 0.3)))
        self.mastery.pragmatics = max(0.0, min(1.0, self.mastery.pragmatics + (0.1 if success else -0.05)))

        self.latencies.append(latency_ms)
        if len(self.latencies) > 10:
            self.latencies.pop(0)
        sorted_lat = sorted(self.latencies)
        self.median_latency_ms = sorted_lat[len(sorted_lat) // 2]
        self.statistics.last_practiced_at = timestamp


class LearnerProfile(BaseModel):
    learner_id: str
    native_language: str = "zh-TW" # "zh-TW", "zh-CN", "en"
    target_language: str = "es"    # "es", "ja", "en"
    current_difficulty_level: int = 1 # 1: Novice (Full Scaffolding), 2: Intermediate (Word Builder Only), 3: Fluent (Blind Direct Input)
    consecutive_global_correct: int = 0
    consecutive_global_errors: int = 0
    skills: Dict[str, LearnerSkillState] = Field(default_factory=dict)
    goals: List[str] = Field(default_factory=list)

    def get_or_create_skill(self, skill_id: str) -> LearnerSkillState:
        if skill_id not in self.skills:
            self.skills[skill_id] = LearnerSkillState(skill_id=skill_id)
        return self.skills[skill_id]

    def update_adaptive_difficulty(self, success: bool):
        """Dynamic difficulty adjustment based on performance streak."""
        if success:
            self.consecutive_global_correct += 1
            self.consecutive_global_errors = 0
            # If 3 consecutive correct and currently at level 1 -> Level 2
            if self.consecutive_global_correct >= 3 and self.current_difficulty_level == 1:
                self.current_difficulty_level = 2
            # If 5 consecutive correct and level 2 -> Level 3
            elif self.consecutive_global_correct >= 6 and self.current_difficulty_level == 2:
                self.current_difficulty_level = 3
        else:
            self.consecutive_global_correct = 0
            self.consecutive_global_errors += 1
            # If error and higher level -> Step down
            if self.consecutive_global_errors >= 1 and self.current_difficulty_level == 3:
                self.current_difficulty_level = 2
            elif self.consecutive_global_errors >= 2 and self.current_difficulty_level == 2:
                self.current_difficulty_level = 1
