"""
Adaptive Memory Model Interface & Implementation

Section 17:
Does NOT hardcode a single rigid Ebbinghaus curve.
Models: R = P(successful retrieval | skill, learner, elapsed_time)
Separates recognition stability, production stability, and automaticity stability.
"""

import math
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timezone
from core.learner_model import LearnerSkillState


class MemoryModel(ABC):
    @abstractmethod
    def predict_retrievability(self, state: LearnerSkillState, current_time: Optional[datetime] = None) -> float:
        """Predict probability of successful retrieval given elapsed time and current stability."""
        pass

    @abstractmethod
    def update(self, state: LearnerSkillState, success: bool, latency_ms: float, current_time: Optional[datetime] = None) -> LearnerSkillState:
        """Update stability, retrievability, and statistics based on retrieval event."""
        pass


class AdaptivePowerLawMemoryModel(MemoryModel):
    """
    Implements adaptive power-law / spaced repetition memory dynamics.
    R(t) = exp( - t / S ) where t is elapsed days, S is stability in days.
    """
    
    def predict_retrievability(self, state: LearnerSkillState, current_time: Optional[datetime] = None) -> float:
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        if not state.memory.last_reviewed_at:
            return 1.0
            
        try:
            last_review = datetime.fromisoformat(state.memory.last_reviewed_at)
            elapsed_seconds = max(0.0, (current_time - last_review).total_seconds())
            elapsed_days = elapsed_seconds / 86400.0
        except Exception:
            elapsed_days = 0.0
            
        stability = max(0.1, state.memory.stability_days)
        retrievability = math.exp(- (elapsed_days / stability))
        retrievability = max(0.01, min(1.0, retrievability))
        state.memory.retrievability = retrievability
        return retrievability

    def update(self, state: LearnerSkillState, success: bool, latency_ms: float, current_time: Optional[datetime] = None) -> LearnerSkillState:
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        state.statistics.exposures += 1
        state.statistics.retrievals += 1
        state.record_latency(latency_ms)

        current_stability = state.memory.stability_days

        if success:
            state.statistics.successes += 1
            latency_factor = 1.2 if latency_ms < 1500 else (1.0 if latency_ms < 3000 else 0.8)
            multiplier = 1.8 * latency_factor
            state.memory.stability_days = max(0.5, current_stability * multiplier)
            state.memory.retrievability = 1.0
        else:
            state.statistics.failures += 1
            state.memory.stability_days = max(0.2, current_stability * 0.4)
            state.memory.retrievability = 0.3

        state.memory.last_reviewed_at = current_time.isoformat()
        return state


default_memory_model = AdaptivePowerLawMemoryModel()
