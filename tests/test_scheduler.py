"""Unit tests for Scheduler & Skill Clustering."""

import unittest
from core.learner_model import LearnerProfile
from core.scheduler import Scheduler
from core.skill_graph import global_skill_graph


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler(global_skill_graph)
        self.profile = LearnerProfile(learner_id="test_user", target_language="ja")

    def test_skill_selection_and_clustering(self):
        cluster = self.scheduler.build_skill_cluster(self.profile, domain="travel")
        self.assertIsNotNone(cluster)
        self.assertTrue(len(cluster.primary) > 0)
        self.assertEqual(cluster.domain, "travel")


if __name__ == "__main__":
    unittest.main()
