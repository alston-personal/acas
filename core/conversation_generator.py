"""
Conversation Generator Interface & Implementation

Section 22:
- Generates natural scenarios & prompts based on Skill Cluster.
- Does NOT explicitly tell the learner what grammar rule is being tested.
- Naturally triggers target skill across various contextual domains.
- Avoids repetitive rote memorization by generating varied prompts.
"""

import random
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from core.scheduler import SkillCluster
from core.learner_model import LearnerProfile
from scenarios.registry import ScenarioRegistry, global_scenarios


class GeneratedPrompt(BaseModel):
    scenario_id: str
    domain: str
    turn_index: int = 1
    prompt_text_ja: str
    prompt_text_en: str
    target_skills: List[str]
    hints: Optional[str] = None
    expected_ir: Dict[str, Any] = {}


class ConversationGenerator:
    def __init__(self, scenario_registry: ScenarioRegistry = global_scenarios):
        self.scenario_registry = scenario_registry

    def generate_scenario_prompt(
        self,
        skill_cluster: SkillCluster,
        profile: LearnerProfile,
        turn_index: int = 1,
    ) -> GeneratedPrompt:
        target_skills = skill_cluster.primary + skill_cluster.secondary
        scenario = self.scenario_registry.find_best_scenario_for_skills(target_skills, domain=skill_cluster.domain)
        
        if not scenario:
            scenario = self.scenario_registry.list_all()[0]

        pdata = scenario.prompt_data
        prompt_ja = pdata.prompts_target.get("ja", "明日雨が降ったら、どうしますか？")
        prompt_en = pdata.translations_native.get("en", "If it rains tomorrow, what will you do?")
        hints = pdata.hints_native.get(profile.native_language, pdata.hints_native.get("zh-TW", ""))
        skills = pdata.target_skills_by_lang.get(profile.target_language, pdata.target_skills_universal)

        return GeneratedPrompt(
            scenario_id=scenario.scenario_id,
            domain=scenario.domain,
            turn_index=turn_index,
            prompt_text_ja=prompt_ja,
            prompt_text_en=prompt_en,
            target_skills=skills,
            hints=hints,
            expected_ir=scenario.expected_ir.model_dump() if hasattr(scenario.expected_ir, 'model_dump') else {},
        )
