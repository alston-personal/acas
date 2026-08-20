"""
Scenario Definitions with Dynamic Multilingual Support.
Cleanly separates target language realizations and native language translations.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from core.ir_schema import CommunicationIR


class MultilingualPrompt(BaseModel):
    prompts_target: Dict[str, str] = Field(default_factory=dict)
    translations_native: Dict[str, str] = Field(default_factory=dict)
    hints_native: Dict[str, str] = Field(default_factory=dict)
    target_skills_universal: List[str] = Field(default_factory=list)
    target_skills_by_lang: Dict[str, List[str]] = Field(default_factory=dict)


class Scenario(BaseModel):
    scenario_id: str
    domain: str
    title_native: Dict[str, str] = Field(default_factory=dict)
    description_native: Dict[str, str] = Field(default_factory=dict)
    prompt_data: MultilingualPrompt
    difficulty_level: int = 1
    expected_ir: CommunicationIR


ScenarioDefinition = Scenario
ScenarioTurnTemplate = MultilingualPrompt
