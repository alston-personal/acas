"""
Adaptive Learning Scheduler v0.1

Section 19, 20, 21, 39:
Priority formula:
  priority = forgetting_risk * communication_utility * weakness * unlock_value * expected_learning_gain
Skill Selection:
  NEW, REVIEW, AUTOMATICITY
Builds Skill Cluster for Conversation Generator.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from core.skill_graph import SkillGraph, UniversalSkill, LanguageSkill, global_skill_graph
from core.learner_model import LearnerProfile, LearnerSkillState
from core.memory_model import MemoryModel, default_memory_model


class SkillCluster(BaseModel):
    primary: List[str]  # e.g. ["JP.CONDITION.TARA"]
    secondary: List[str] = Field(default_factory=list)  # e.g. ["JP.CAUSE.KARA"]
    automaticity: List[str] = Field(default_factory=list)  # e.g. ["JP.DESIRE.TAI"]
    domain: str = "travel"
    difficulty: float = 0.45


class Scheduler:
    def __init__(self, skill_graph: SkillGraph = global_skill_graph, memory_model: MemoryModel = default_memory_model):
        self.skill_graph = skill_graph
        self.memory_model = memory_model

    def calculate_priority(self, skill: LanguageSkill, learner_state: LearnerSkillState) -> Tuple[float, Dict[str, float]]:
        # 1. Forgetting risk = 1 - predicted_retrievability
        retrievability = self.memory_model.predict_retrievability(learner_state)
        forgetting_risk = max(0.05, 1.0 - retrievability)

        # 2. Weakness = 1 - overall_mastery
        mastery = learner_state.mastery.overall_mastery
        weakness = max(0.05, 1.0 - mastery)

        # 3. Communication utility
        utility = skill.communication_utility

        # 4. Unlock value (how many downstream skills depend on this)
        unlock_val = 0.8  # default high unlock

        # 5. Expected learning gain (diminishing returns as mastery approaches 1.0)
        expected_learning_gain = max(0.1, 1.0 - (mastery * 0.8))

        # Overall priority
        priority = forgetting_risk * utility * weakness * unlock_val * expected_learning_gain

        metrics = {
            "priority": priority,
            "forgetting_risk": forgetting_risk,
            "retrievability": retrievability,
            "mastery": mastery,
            "weakness": weakness,
            "utility": utility,
            "unlock_val": unlock_val,
            "expected_learning_gain": expected_learning_gain,
        }
        return priority, metrics

    def select_session_skills(self, profile: LearnerProfile, language: str = "ja") -> Dict[str, List[str]]:
        new_candidates = []
        review_candidates = []
        auto_candidates = []

        all_lang_skills = [s for s in self.skill_graph.language_skills.values() if s.language == language]

        for skill in all_lang_skills:
            state = profile.get_or_create_skill_state(skill.skill_id)
            priority, metrics = self.calculate_priority(skill, state)

            if state.statistics.exposures == 0:
                # Completely new
                new_candidates.append((priority, skill.skill_id))
            elif state.mastery.production > 0.75 and state.median_latency_ms > 1500:
                # Known but needs automaticity/speed training
                auto_candidates.append((priority, skill.skill_id))
            else:
                # In active learning or review
                review_candidates.append((priority, skill.skill_id))

        new_candidates.sort(reverse=True)
        review_candidates.sort(reverse=True)
        auto_candidates.sort(reverse=True)

        selected_new = [sid for _, sid in new_candidates[:1]] or ([all_lang_skills[0].skill_id] if all_lang_skills else [])
        selected_review = [sid for _, sid in review_candidates[:2]]
        selected_auto = [sid for _, sid in auto_candidates[:1]]

        return {
            "new": selected_new,
            "review": selected_review,
            "automaticity": selected_auto,
        }

    def build_skill_cluster(self, profile: LearnerProfile, domain: str = "travel", language: str = "ja") -> SkillCluster:
        selection = self.select_session_skills(profile, language=language)
        
        # Primary is usually the top new or highest review priority skill
        primary = selection["new"] or selection["review"][:1] or ["JP.CONDITION.TARA"]
        secondary = [s for s in selection["review"] if s not in primary]
        automaticity = selection["automaticity"]

        # Calculate average difficulty
        skills = [self.skill_graph.get_skill(s) for s in primary + secondary + automaticity if self.skill_graph.get_skill(s)]
        diff = sum(getattr(s, "difficulty", 0.4) for s in skills) / max(1, len(skills))

        return SkillCluster(
            primary=primary,
            secondary=secondary,
            automaticity=automaticity,
            domain=domain,
            difficulty=round(diff, 2),
        )
