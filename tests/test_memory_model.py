"""Unit tests for Adaptive Memory Model & Retrievability Prediction."""

import unittest
from datetime import datetime, timezone, timedelta
from core.learner_model import LearnerSkillState
from core.memory_model import AdaptivePowerLawMemoryModel


class TestMemoryModel(unittest.TestCase):
    def setUp(self):
        self.model = AdaptivePowerLawMemoryModel()
        self.state = LearnerSkillState(learner_id="test_user", skill_id="JP.CONDITION.TARA")

    def test_initial_retrievability(self):
        r = self.model.predict_retrievability(self.state)
        self.assertEqual(r, 1.0)

    def test_retrieval_success_increases_stability(self):
        initial_stability = self.state.memory.stability_days
        self.model.update(self.state, success=True, latency_ms=1200.0)
        self.assertGreater(self.state.memory.stability_days, initial_stability)
        self.assertEqual(self.state.statistics.successes, 1)

    def test_retrieval_failure_drops_stability(self):
        self.state.memory.stability_days = 10.0
        self.model.update(self.state, success=False, latency_ms=4500.0)
        self.assertLess(self.state.memory.stability_days, 10.0)
        self.assertEqual(self.state.statistics.failures, 1)


if __name__ == "__main__":
    unittest.main()
