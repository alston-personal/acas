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
from scenarios.definitions import ScenarioDefinition, ScenarioTurnTemplate


class GeneratedPrompt(BaseModel):
    scenario_id: str
    domain: str
    turn_index: int
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
            scenario = self.scenario_registry.get_all()[0]

        turns = scenario.turns
        turn = None
        for t in turns:
            if t.turn_id == turn_index:
                turn = t
                break
        if not turn:
            turn = turns[0] if turns else ScenarioTurnTemplate(
                turn_id=1,
                ai_prompt_text_ja="日本に住むなら、どこに住みたい？",
                ai_prompt_text_en="If you were to live in Japan, where would you want to live?",
                target_skills=["JP.CONDITION.NARA", "JP.DESIRE.TAI"],
                expected_ir_pattern={"predicate": "LIVE"},
                hints="Answer naturally with condition and preference.",
            )

        return GeneratedPrompt(
            scenario_id=scenario.scenario_id,
            domain=scenario.domain,
            turn_index=turn.turn_id,
            prompt_text_ja=turn.ai_prompt_text_ja,
            prompt_text_en=turn.ai_prompt_text_en,
            target_skills=turn.target_skills,
            hints=turn.hints,
            expected_ir=turn.expected_ir_pattern,
        )
