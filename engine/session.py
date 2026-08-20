"""
ACAS Learning Session Engine

Section 31 & Section 40:
Full closed learning loop:
1. Load Goal & Learner Profile
2. Predict current memory state (retrievability)
3. Generate candidate skills & rank by priority/expected gain
4. Build Skill Cluster (NEW, REVIEW, AUTOMATICITY)
5. Generate Scenario & Prompt
6. Collect User Response & Latency
7. Performance Analyzer evaluates response (semantics, grammar, pragmatics)
8. Emit structured LearningEvents
9. Update Learner State & Memory Model
10. Recalculate and repeat
"""

from typing import Dict, List, Optional
from core.goal import LearningGoal, GoalProgress, ProgressDimensions
from core.learner_model import LearnerProfile, LearnerSkillState
from core.memory_model import MemoryModel, default_memory_model
from core.skill_graph import SkillGraph, global_skill_graph
from core.scheduler import Scheduler, SkillCluster
from core.conversation_generator import ConversationGenerator, GeneratedPrompt
from core.performance_analyzer import PerformanceAnalyzer, PerformanceAnalysisResult
from core.learning_events import LearningEvent, LearningEventStore


class ACASSessionEngine:
    def __init__(
        self,
        learner_id: str = "user_001",
        goal: Optional[LearningGoal] = None,
        event_store: Optional[LearningEventStore] = None,
    ):
        self.learner_id = learner_id
        self.goal = goal or LearningGoal()
        self.profile = LearnerProfile(learner_id=learner_id, target_language=self.goal.language)
        self.event_store = event_store or LearningEventStore()
        
        self.skill_graph = global_skill_graph
        self.memory_model = default_memory_model
        self.scheduler = Scheduler(self.skill_graph, self.memory_model)
        self.conversation_gen = ConversationGenerator()
        self.analyzer = PerformanceAnalyzer()

        self.current_prompt: Optional[GeneratedPrompt] = None
        self.current_cluster: Optional[SkillCluster] = None
        self.session_turn_count: int = 0

    def start_next_turn(self, domain: Optional[str] = None) -> GeneratedPrompt:
        """Steps 1-7: Prepare the next learning interaction."""
        self.session_turn_count += 1

        for state in self.profile.skills.values():
            self.memory_model.predict_retrievability(state)

        chosen_domain = domain or self.goal.domains[(self.session_turn_count - 1) % len(self.goal.domains)]
        self.current_cluster = self.scheduler.build_skill_cluster(self.profile, domain=chosen_domain, language=self.goal.language)

        self.current_prompt = self.conversation_gen.generate_scenario_prompt(
            self.current_cluster,
            self.profile,
            turn_index=self.session_turn_count,
        )
        return self.current_prompt

    def process_response(self, response_text: str, latency_ms: float) -> PerformanceAnalysisResult:
        """Steps 8-12: Analyze response, emit events, update learner state & memory."""
        if not self.current_prompt:
            raise ValueError("No active prompt. Call start_next_turn() first.")

        analysis = self.analyzer.analyze_response(
            prompt_text=self.current_prompt.prompt_text_ja,
            target_skills=self.current_prompt.target_skills,
            response_text=response_text,
            latency_ms=latency_ms,
            learner_id=self.learner_id,
            scenario_id=self.current_prompt.scenario_id,
        )

        if analysis.learning_event:
            self.event_store.record(analysis.learning_event)

            for sk_obs in analysis.learning_event.skills:
                state = self.profile.get_or_create_skill_state(sk_obs.skill_id)
                
                if sk_obs.dimension == "production":
                    delta = 0.15 if sk_obs.success else -0.05
                    state.mastery.production = max(0.0, min(1.0, state.mastery.production + delta))
                elif sk_obs.dimension == "recognition":
                    state.mastery.recognition = max(0.0, min(1.0, state.mastery.recognition + 0.10))

                state.mastery.pragmatics = max(0.0, min(1.0, state.mastery.pragmatics + 0.08))
                state.mastery.composition = max(0.0, min(1.0, state.mastery.composition + 0.10))

                self.memory_model.update(state, success=sk_obs.success, latency_ms=latency_ms)

        return analysis

    def compute_progress(self) -> GoalProgress:
        """Compute progress across multidimensional mastery vector."""
        all_skills = list(self.skill_graph.language_skills.values())
        total = len(all_skills)
        if total == 0:
            return GoalProgress(goal_id=self.goal.goal_id)

        rec_sum = 0.0
        prod_sum = 0.0
        auto_sum = 0.0
        ret_sum = 0.0
        prag_sum = 0.0
        mastered_count = 0

        for s in all_skills:
            st = self.profile.get_or_create_skill_state(s.skill_id)
            rec_sum += st.mastery.recognition
            prod_sum += st.mastery.production
            prag_sum += st.mastery.pragmatics
            ret_sum += self.memory_model.predict_retrievability(st)
            
            auto_val = 1.0 if st.is_fluent() else (st.mastery.production * 0.5)
            auto_sum += auto_val
            
            if st.mastery.overall_mastery >= 0.85 and st.memory.retrievability >= 0.8:
                mastered_count += 1

        rec_avg = rec_sum / total
        prod_avg = prod_sum / total
        auto_avg = auto_sum / total
        ret_avg = ret_sum / total
        prag_avg = prag_sum / total
        coverage = len([s for s in all_skills if self.profile.get_or_create_skill_state(s.skill_id).statistics.exposures > 0]) / total

        overall = (rec_avg * 0.2 + prod_avg * 0.3 + auto_avg * 0.2 + ret_avg * 0.2 + prag_avg * 0.1)

        return GoalProgress(
            goal_id=self.goal.goal_id,
            overall=round(overall, 3),
            dimensions=ProgressDimensions(
                coverage=round(coverage, 3),
                recognition=round(rec_avg, 3),
                listening=round(rec_avg * 0.9, 3),
                production=round(prod_avg, 3),
                automaticity=round(auto_avg, 3),
                pragmatics=round(prag_avg, 3),
                retention=round(ret_avg, 3),
            ),
            mastered_skills_count=mastered_count,
            total_skills_count=total,
        )
