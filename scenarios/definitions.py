"""
Scenario Definitions with Dynamic Multilingual Support.
Cleanly separates target language realizations and native language translations.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from core.ir_schema import CommunicationIR


class MultilingualPrompt(BaseModel):
    # Target Language Prompts
    prompts_target: Dict[str, str] = Field(default_factory=dict) # e.g. {"ja": "...", "es": "...", "en": "..."}
    # Native Language Translations
    translations_native: Dict[str, str] = Field(default_factory=dict) # e.g. {"zh-TW": "...", "zh-CN": "...", "en": "..."}
    # Native Language Hints
    hints_native: Dict[str, str] = Field(default_factory=dict) # e.g. {"zh-TW": "...", "zh-CN": "...", "en": "..."}
    
    target_skills_universal: List[str] = Field(default_factory=list) # e.g. ["CORE.CONDITION", "CORE.NEGATION"]
    target_skills_by_lang: Dict[str, List[str]] = Field(default_factory=dict) # {"ja": ["JP.CONDITION.TARA"], "es": ["ES.CONDITION.SI"]}


class Scenario(BaseModel):
    scenario_id: str
    domain: str
    title_native: Dict[str, str] = Field(default_factory=dict)
    description_native: Dict[str, str] = Field(default_factory=dict)
    prompt_data: MultilingualPrompt
    difficulty_level: int = 1 # 1: Novice, 2: Intermediate, 3: Advanced
    expected_ir: CommunicationIR
