"""
Performance Analyzer Implementation

Section 23:
Analyzes user response:
- Semantic correctness
- Grammar accuracy
- Naturalness
- Pragmatic appropriateness
- Latency (ms)
- Detected skills
Emits structured LearningEvents (Section 16).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.ir_schema import CommunicationIR
from core.learner_model import LearnerProfile
from core.learning_events import (
    LearningEvent,
    PromptTarget,
    ResponseObservation,
    PerformanceObservations,
    SkillObservation,
)
from languages.ja.adapter import JapaneseAdapter
from languages.base import Evaluation


class PerformanceAnalysisResult(BaseModel):
    semantic_correctness: float = Field(default=0.9, ge=0.0, le=1.0)
    grammar_accuracy: float = Field(default=0.9, ge=0.0, le=1.0)
    naturalness: float = Field(default=0.9, ge=0.0, le=1.0)
    pragmatic_appropriateness: float = Field(default=0.9, ge=0.0, le=1.0)
    detected_skills: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    skill_observations: List[SkillObservation] = Field(default_factory=list)
    parsed_ir: Optional[Dict[str, Any]] = None
    learning_event: Optional[LearningEvent] = None


class PerformanceAnalyzer:
    def __init__(self, adapter: Optional[JapaneseAdapter] = None):
        self.adapter = adapter or JapaneseAdapter()

    def analyze_response(
        self,
        prompt_text: str,
        target_skills: List[str],
        response_text: str,
        latency_ms: float,
        learner_id: str = "user_001",
        scenario_id: str = "general",
    ) -> PerformanceAnalysisResult:
        clean_response = response_text.strip()

        if not clean_response:
            obs = PerformanceObservations(understanding=0.0, grammar=0.0, naturalness=0.0, pragmatics=0.0)
            event = LearningEvent(
                learner_id=learner_id,
                scenario=scenario_id,
                prompt=PromptTarget(text=prompt_text, target_skills=target_skills),
                response=ResponseObservation(text="", latency_ms=latency_ms),
                observations=obs,
                skills=[SkillObservation(skill_id=s, dimension="production", success=False, score=0.0) for s in target_skills],
            )
            return PerformanceAnalysisResult(
                semantic_correctness=0.0,
                grammar_accuracy=0.0,
                naturalness=0.0,
                pragmatic_appropriateness=0.0,
                detected_skills=[],
                errors=["No input received"],
                learning_event=event,
            )

        parsed_ir = self.adapter.parse(clean_response)
        ir_dict = parsed_ir.model_dump()

        eval_result = self.adapter.evaluate_naturalness(clean_response, parsed_ir)
        detected_skills = eval_result.detected_skills
        matched_target_skills = set(target_skills).intersection(set(detected_skills))

        semantic_correctness = 0.95 if (len(matched_target_skills) > 0 or len(clean_response) > 2) else 0.70
        grammar_accuracy = eval_result.grammar_score
        naturalness = eval_result.naturalness_score
        pragmatic_appropriateness = eval_result.pragmatic_score

        skill_observations = []
        for ts in target_skills:
            success = (ts in detected_skills) or (grammar_accuracy > 0.85)
            skill_observations.append(
                SkillObservation(
                    skill_id=ts,
                    dimension="production",
                    success=success,
                    score=1.0 if success else 0.4,
                    notes="Successfully produced pattern" if success else "Target pattern not fully matched",
                )
            )

        for ts in target_skills:
            skill_observations.append(
                SkillObservation(
                    skill_id=ts,
                    dimension="recognition",
                    success=True,
                    score=0.95,
                    notes="Understood contextual prompt",
                )
            )

        obs = PerformanceObservations(
            understanding=0.95,
            grammar=grammar_accuracy,
            naturalness=naturalness,
            pragmatics=pragmatic_appropriateness,
        )

        learning_event = LearningEvent(
            learner_id=learner_id,
            scenario=scenario_id,
            prompt=PromptTarget(text=prompt_text, target_skills=target_skills),
            response=ResponseObservation(text=clean_response, latency_ms=latency_ms),
            observations=obs,
            skills=skill_observations,
            raw_ir=ir_dict,
        )

        return PerformanceAnalysisResult(
            semantic_correctness=semantic_correctness,
            grammar_accuracy=grammar_accuracy,
            naturalness=naturalness,
            pragmatic_appropriateness=pragmatic_appropriateness,
            detected_skills=detected_skills,
            errors=eval_result.feedback,
            skill_observations=skill_observations,
            parsed_ir=ir_dict,
            learning_event=learning_event,
        )
