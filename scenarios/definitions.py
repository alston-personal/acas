"""
Multi-turn Contextual Story Episodes (SLA Coherent Scenarios).
Ensures conversational continuity within a thematic storyline.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from core.ir_schema import CommunicationIR


class EpisodeTurn(BaseModel):
    turn_id: int
    step_title: Dict[str, str] = Field(default_factory=dict) # {"zh-TW": "第 1 幕：入座與確認預約", ...}
    prompts_target: Dict[str, str] = Field(default_factory=dict) # {"es": "...", "ja": "...", "en": "..."}
    translations_native: Dict[str, str] = Field(default_factory=dict) # {"zh-TW": "...", ...}
    hints_native: Dict[str, str] = Field(default_factory=dict)
    formula: Dict[str, str] = Field(default_factory=dict)
    target_skills_universal: List[str] = Field(default_factory=list)
    target_skills_by_lang: Dict[str, List[str]] = Field(default_factory=dict)
    choices_by_lang: Dict[str, List[str]] = Field(default_factory=dict)
    words_by_lang: Dict[str, List[Dict[str, str]]] = Field(default_factory=dict)


class ScenarioEpisode(BaseModel):
    episode_id: str
    icon: str = "🍽️"
    domain: str = "travel"
    title_native: Dict[str, str] = Field(default_factory=dict)
    description_native: Dict[str, str] = Field(default_factory=dict)
    turns: List[EpisodeTurn] = Field(default_factory=list)


# Aliases for backwards compatibility
Scenario = ScenarioEpisode
ScenarioDefinition = ScenarioEpisode
ScenarioTurnTemplate = EpisodeTurn
