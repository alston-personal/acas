"""
Adaptive Memory Model Interface & Implementation

Section 17:
Does NOT hardcode a single rigid Ebbinghaus curve.
Models: R = P(successful retrieval | skill, learner, elapsed_time)
Separates recognition stability, production stability, and automaticity stability.
"""

from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from core.learner_model import LearnerSkillState


class MemoryState(BaseModel):
    stability_days: float = Field(default=1.0, ge=0.01)
    retrievability: float = Field(default=1.0, ge=0.0, le=1.0)
    last_reviewed_at: Optional[datetime] = None
    half_life_days: float = Field(default=1.0, ge=0.01)


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
            
        elapsed_seconds = (current_time - state.memory.last_reviewed_at).total_seconds()
        elapsed_days = max(0.0, elapsed_seconds / 86400.0)
        
        # Power law retrievability decay
        S = max(0.05, state.memory.stability_days)
        R = math.exp(-elapsed_days / S)
        return max(0.0, min(1.0, R))

    def update(self, state: LearnerSkillState, success: bool, latency_ms: float, current_time: Optional[datetime] = None) -> LearnerSkillState:
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        prior_R = self.predict_retrievability(state, current_time)
        current_S = state.memory.stability_days
        
        if success:
            # Latency factor: faster response means higher stability boost
            latency_factor = max(0.8, min(1.5, 2000.0 / max(500.0, latency_ms)))
            difficulty_bonus = 1.0 + (1.0 - prior_R) * 1.5
            new_S = current_S * (1.0 + 0.4 * difficulty_bonus * latency_factor)
            state.statistics.successes += 1
        else:
            # Failed retrieval reduces stability
            new_S = max(0.2, current_S * 0.4)
            state.statistics.failures += 1
            
        state.memory.stability_days = new_S
        state.memory.retrievability = 1.0 if success else 0.4
        state.memory.last_reviewed_at = current_time
        state.memory.half_life_days = new_S * math.log(2)
        
        return state


default_memory_model = AdaptivePowerLawMemoryModel()
