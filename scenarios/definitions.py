"""
Scenario Schema and Definitions

Section 27 & Section 28:
Defines rich scenario metadata and contextual conversational templates.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ScenarioTurnTemplate(BaseModel):
    turn_id: int
    ai_prompt_text_ja: str
    ai_prompt_text_en: str
    target_skills: List[str]
    expected_ir_pattern: Dict[str, Any]
    hints: Optional[str] = None


class ScenarioDefinition(BaseModel):
    scenario_id: str  # e.g. "travel.restaurant.order"
    domain: str  # "travel", "daily_life", "food", "weather"
    title: str
    description: str
    required_skills: List[str]  # e.g. ["CORE.REQUEST", "CORE.QUANTITY"]
    language_skills: List[str]  # e.g. ["JP.REQUEST.KUDASAI"]
    vocabulary_domains: List[str]  # e.g. ["food", "restaurant"]
    difficulty: float = 0.20
    turns: List[ScenarioTurnTemplate] = Field(default_factory=list)
