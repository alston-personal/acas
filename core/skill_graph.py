"""
Skill Graph and Skill Definition

Defines Universal Skills (e.g. CORE.CONDITION) vs Language-specific Skills (e.g. JP.CONDITION.TARA, ES.CONDITION.SI)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class UniversalSkill(BaseModel):
    skill_id: str
    type: str = "universal"
    concept: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    communication_utility: float = Field(default=0.8, ge=0.0, le=1.0)
    composition_value: float = Field(default=0.8, ge=0.0, le=1.0)
    unlock_value: float = Field(default=0.5, ge=0.0, le=1.0)


class LanguageSkill(BaseModel):
    skill_id: str
    language: str  # "ja", "en", "es", "zh"
    concept: str
    realization: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    frequency: float = Field(default=0.8, ge=0.0, le=1.0)
    difficulty: float = Field(default=0.4, ge=0.0, le=1.0)
    communication_utility: float = Field(default=0.8, ge=0.0, le=1.0)


class SkillGraph:
    def __init__(self):
        self.universal_skills: Dict[str, UniversalSkill] = {}
        self.language_skills: Dict[str, LanguageSkill] = {}
        self._init_mvp_skills()

    def register_universal(self, skill: UniversalSkill):
        self.universal_skills[skill.skill_id] = skill

    def register_language(self, skill: LanguageSkill):
        self.language_skills[skill.skill_id] = skill

    def get_skill(self, skill_id: str) -> Optional[UniversalSkill | LanguageSkill]:
        if skill_id in self.universal_skills:
            return self.universal_skills[skill_id]
        return self.language_skills.get(skill_id)

    def get_all_skills(self) -> List[UniversalSkill | LanguageSkill]:
        return list(self.universal_skills.values()) + list(self.language_skills.values())

    def get_language_skills_by_concept(self, concept: str, language: str = "ja") -> List[LanguageSkill]:
        return [
            s for s in self.language_skills.values()
            if s.concept == concept and s.language == language
        ]

    def _init_mvp_skills(self):
        mvp_universal = [
            UniversalSkill(skill_id="CORE.INFORM", concept="INFORM", description="Provide factual information", dependencies=[], communication_utility=0.98, composition_value=0.9, unlock_value=0.9),
            UniversalSkill(skill_id="CORE.ASK", concept="ASK", description="Ask a question or elicit info", dependencies=["CORE.INFORM"], communication_utility=0.98, composition_value=0.9, unlock_value=0.95),
            UniversalSkill(skill_id="CORE.NEGATION", concept="NEGATION", description="Negate a predicate, state, or event", dependencies=["CORE.INFORM"], communication_utility=0.95, composition_value=0.95, unlock_value=0.9),
            UniversalSkill(skill_id="CORE.TIME", concept="TIME", description="Temporal orientation (past, present, future)", dependencies=["CORE.INFORM"], communication_utility=0.92, composition_value=0.9, unlock_value=0.85),
            UniversalSkill(skill_id="CORE.LOCATION", concept="LOCATION", description="Spatial orientation and destinations", dependencies=["CORE.INFORM"], communication_utility=0.92, composition_value=0.85, unlock_value=0.8),
            UniversalSkill(skill_id="CORE.DESIRE", concept="DESIRE", description="Express want, wish, or desire", dependencies=["CORE.INFORM"], communication_utility=0.94, composition_value=0.88, unlock_value=0.85),
            UniversalSkill(skill_id="CORE.ABILITY", concept="ABILITY", description="Express ability or possibility to act", dependencies=["CORE.INFORM"], communication_utility=0.90, composition_value=0.85, unlock_value=0.8),
            UniversalSkill(skill_id="CORE.EXPERIENCE", concept="EXPERIENCE", description="Express past experiences", dependencies=["CORE.TIME"], communication_utility=0.88, composition_value=0.85, unlock_value=0.8),
            UniversalSkill(skill_id="CORE.OPINION", concept="OPINION", description="Express subjective thoughts or opinions", dependencies=["CORE.INFORM"], communication_utility=0.90, composition_value=0.9, unlock_value=0.85),
            UniversalSkill(skill_id="CORE.POSSIBILITY", concept="POSSIBILITY", description="Express probability or uncertainty", dependencies=["CORE.OPINION"], communication_utility=0.86, composition_value=0.85, unlock_value=0.75),
            UniversalSkill(skill_id="CORE.CAUSE", concept="CAUSE", description="Express reasons and causality (cause & effect)", dependencies=["CORE.INFORM"], communication_utility=0.92, composition_value=0.95, unlock_value=0.9),
            UniversalSkill(skill_id="CORE.CONDITION", concept="CONDITION", description="Hypothetical and conditional relations", dependencies=["CORE.INFORM"], communication_utility=0.92, composition_value=0.95, unlock_value=0.9),
            UniversalSkill(skill_id="CORE.COMPARISON", concept="COMPARISON", description="Compare properties or choices", dependencies=["CORE.INFORM"], communication_utility=0.85, composition_value=0.8, unlock_value=0.75),
            UniversalSkill(skill_id="CORE.REQUEST", concept="REQUEST", description="Politely ask someone to perform an action", dependencies=["CORE.ASK"], communication_utility=0.96, composition_value=0.9, unlock_value=0.9),
            UniversalSkill(skill_id="CORE.SUGGEST", concept="SUGGEST", description="Propose an idea or action", dependencies=["CORE.INFORM"], communication_utility=0.88, composition_value=0.85, unlock_value=0.8),
            UniversalSkill(skill_id="CORE.AGREE", concept="AGREE", description="Express agreement or consensus", dependencies=["CORE.INFORM"], communication_utility=0.90, composition_value=0.75, unlock_value=0.7),
            UniversalSkill(skill_id="CORE.DISAGREE", concept="DISAGREE", description="Express disagreement or dissent", dependencies=["CORE.NEGATION"], communication_utility=0.88, composition_value=0.8, unlock_value=0.75),
            UniversalSkill(skill_id="CORE.CONFIRM", concept="CONFIRM", description="Verify understanding or check facts", dependencies=["CORE.ASK"], communication_utility=0.92, composition_value=0.85, unlock_value=0.8),
            UniversalSkill(skill_id="CORE.CLARIFY", concept="CLARIFY", description="Seek or provide clarification", dependencies=["CORE.ASK"], communication_utility=0.90, composition_value=0.85, unlock_value=0.8),
            UniversalSkill(skill_id="CORE.REPAIR", concept="REPAIR", description="Correct misunderstandings or slips", dependencies=["CORE.CLARIFY"], communication_utility=0.85, composition_value=0.8, unlock_value=0.75),
        ]
        for us in mvp_universal:
            self.register_universal(us)

        # Japanese Skills
        ja_skills = [
            LanguageSkill(skill_id="JP.INFORM.DESU", language="ja", concept="INFORM", realization="～です / ～ます", description="Standard polite assertion", dependencies=["CORE.INFORM"], frequency=0.99, difficulty=0.1, communication_utility=0.99),
            LanguageSkill(skill_id="JP.ASK.KA", language="ja", concept="ASK", realization="～か", description="Question particle", dependencies=["CORE.ASK"], frequency=0.98, difficulty=0.1, communication_utility=0.98),
            LanguageSkill(skill_id="JP.NEGATION.NAI", language="ja", concept="NEGATION", realization="～ない / ～ません", description="Negative verb/adjective forms", dependencies=["CORE.NEGATION"], frequency=0.95, difficulty=0.25, communication_utility=0.95),
            LanguageSkill(skill_id="JP.REQUEST.KUDASAI", language="ja", concept="REQUEST", realization="～てください / ～をください", description="Polite request form", dependencies=["CORE.REQUEST"], frequency=0.95, difficulty=0.2, communication_utility=0.96),
            LanguageSkill(skill_id="JP.DESIRE.TAI", language="ja", concept="DESIRE", realization="～たい", description="Desire to perform action", dependencies=["CORE.DESIRE"], frequency=0.92, difficulty=0.25, communication_utility=0.94),
            LanguageSkill(skill_id="JP.CAUSE.KARA", language="ja", concept="CAUSE", realization="～から / ～ので", description="Expressing reason and causality", dependencies=["CORE.CAUSE"], frequency=0.90, difficulty=0.35, communication_utility=0.92),
            LanguageSkill(skill_id="JP.CONDITION.TARA", language="ja", concept="CONDITION", realization="～たら", description="General condition & temporal sequence", dependencies=["CORE.CONDITION"], frequency=0.90, difficulty=0.45, communication_utility=0.92),
            LanguageSkill(skill_id="JP.CONDITION.NARA", language="ja", concept="CONDITION", realization="～なら", description="Contextual condition / topical condition", dependencies=["CORE.CONDITION"], frequency=0.85, difficulty=0.45, communication_utility=0.88),
            LanguageSkill(skill_id="JP.EXPERIENCE.TAKOTOGAARU", language="ja", concept="EXPERIENCE", realization="～たことがある", description="Past life experience", dependencies=["CORE.EXPERIENCE"], frequency=0.85, difficulty=0.4, communication_utility=0.88),
            LanguageSkill(skill_id="JP.ABILITY.KOTOGADEKIRU", language="ja", concept="ABILITY", realization="～ことができる / 可能形", description="Ability or possibility to do something", dependencies=["CORE.ABILITY"], frequency=0.88, difficulty=0.4, communication_utility=0.90),
            LanguageSkill(skill_id="JP.OPINION.TOOMOU", language="ja", concept="OPINION", realization="～と思う", description="Subjective opinion or impression", dependencies=["CORE.OPINION"], frequency=0.92, difficulty=0.3, communication_utility=0.92),
            LanguageSkill(skill_id="JP.POSSIBILITY.KAMOSHIRENAI", language="ja", concept="POSSIBILITY", realization="～かもしれない", description="Possibility / uncertainty", dependencies=["CORE.POSSIBILITY"], frequency=0.85, difficulty=0.4, communication_utility=0.86),
            LanguageSkill(skill_id="JP.SUGGEST.MASHOU", language="ja", concept="SUGGEST", realization="～ましょう / ～ませんか", description="Suggestion or invitation", dependencies=["CORE.SUGGEST"], frequency=0.88, difficulty=0.25, communication_utility=0.90),
            LanguageSkill(skill_id="JP.CONFIRM.DESHOU", language="ja", concept="CONFIRM", realization="～でしょう / ～よね", description="Confirmation seeker", dependencies=["CORE.CONFIRM"], frequency=0.90, difficulty=0.25, communication_utility=0.92),
        ]
        for js in ja_skills:
            self.register_language(js)

        # Spanish Skills (ES)
        es_skills = [
            LanguageSkill(skill_id="ES.INFORM.PRESENTE", language="es", concept="INFORM", realization="Presente Indicativo", description="Direct statement in Spanish", dependencies=["CORE.INFORM"], frequency=0.99, difficulty=0.15, communication_utility=0.99),
            LanguageSkill(skill_id="ES.ASK.INTERROGATIVE", language="es", concept="ASK", realization="¿...? / Preguntas", description="Questions in Spanish", dependencies=["CORE.ASK"], frequency=0.98, difficulty=0.1, communication_utility=0.98),
            LanguageSkill(skill_id="ES.NEGATION.NO", language="es", concept="NEGATION", realization="No + [verbo]", description="Negative verbs and statements", dependencies=["CORE.NEGATION"], frequency=0.98, difficulty=0.1, communication_utility=0.98),
            LanguageSkill(skill_id="ES.REQUEST.PORFAVOR", language="es", concept="REQUEST", realization="Por favor / ¿Puede...?", description="Polite requests", dependencies=["CORE.REQUEST"], frequency=0.95, difficulty=0.2, communication_utility=0.96),
            LanguageSkill(skill_id="ES.DESIRE.QUIERO", language="es", concept="DESIRE", realization="Quiero + [infinitivo]", description="Expressing desire / wish", dependencies=["CORE.DESIRE"], frequency=0.94, difficulty=0.2, communication_utility=0.95),
            LanguageSkill(skill_id="ES.CAUSE.PORQUE", language="es", concept="CAUSE", realization="Porque + [oración]", description="Expressing causality and reason", dependencies=["CORE.CAUSE"], frequency=0.90, difficulty=0.25, communication_utility=0.92),
            LanguageSkill(skill_id="ES.CONDITION.SI", language="es", concept="CONDITION", realization="Si + [presente], [futuro/presente]", description="Real & hypothetical conditions", dependencies=["CORE.CONDITION"], frequency=0.92, difficulty=0.35, communication_utility=0.94),
            LanguageSkill(skill_id="ES.EXPERIENCE.HABER", language="es", concept="EXPERIENCE", realization="He + [participio] (Pretérito Perfecto)", description="Past life experiences", dependencies=["CORE.EXPERIENCE"], frequency=0.88, difficulty=0.4, communication_utility=0.90),
            LanguageSkill(skill_id="ES.OPINION.CREO", language="es", concept="OPINION", realization="Creo que... / Pienso que...", description="Personal opinions", dependencies=["CORE.OPINION"], frequency=0.90, difficulty=0.25, communication_utility=0.90),
        ]
        for es in es_skills:
            self.register_language(es)


global_skill_graph = SkillGraph()
