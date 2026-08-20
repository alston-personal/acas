"""
Goal and Multidimensional Progress Representation

Section 25 & Section 26:
Replaces linear "Lesson 17 / 100" with multidimensional mastery progress vectors.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GoalRequirements(BaseModel):
    scenario_coverage: float = 0.90
    recognition: float = 0.95
    listening: float = 0.90
    production: float = 0.90
    pragmatics: float = 0.85
    retention_30d: float = 0.90
    median_response_latency_ms: float = 1500.0


class LearningGoal(BaseModel):
    goal_id: str = "JP_DAILY_CONVERSATION"
    display_name: str = "Japanese Daily Conversation Mastery"
    language: str = "ja"
    domains: List[str] = Field(default_factory=lambda: ["daily_life", "travel", "friends", "food", "directions"])
    requirements: GoalRequirements = Field(default_factory=GoalRequirements)


class ProgressDimensions(BaseModel):
    coverage: float = 0.0
    recognition: float = 0.0
    listening: float = 0.0
    production: float = 0.0
    automaticity: float = 0.0
    pragmatics: float = 0.0
    retention: float = 0.0


class GoalProgress(BaseModel):
    goal_id: str
    overall: float = 0.0
    dimensions: ProgressDimensions = Field(default_factory=ProgressDimensions)
    mastered_skills_count: int = 0
    total_skills_count: int = 0
