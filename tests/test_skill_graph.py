"""Unit tests for Skill Graph and 20 MVP Universal Skills."""

import unittest
from core.skill_graph import global_skill_graph, UniversalSkill, LanguageSkill


class TestSkillGraph(unittest.TestCase):
    def test_20_universal_skills_present(self):
        expected_skills = [
            "CORE.INFORM", "CORE.ASK", "CORE.NEGATION", "CORE.TIME", "CORE.LOCATION",
            "CORE.DESIRE", "CORE.ABILITY", "CORE.EXPERIENCE", "CORE.OPINION", "CORE.POSSIBILITY",
            "CORE.CAUSE", "CORE.CONDITION", "CORE.COMPARISON", "CORE.REQUEST", "CORE.SUGGEST",
            "CORE.AGREE", "CORE.DISAGREE", "CORE.CONFIRM", "CORE.CLARIFY", "CORE.REPAIR",
        ]
        for sk in expected_skills:
            skill = global_skill_graph.get_skill(sk)
            self.assertIsNotNone(skill, f"Missing universal skill: {sk}")
            self.assertIsInstance(skill, UniversalSkill)

    def test_japanese_mappings(self):
        tara = global_skill_graph.get_skill("JP.CONDITION.TARA")
        self.assertIsNotNone(tara)
        self.assertEqual(tara.concept, "CONDITION")
        self.assertIn("CORE.CONDITION", tara.dependencies)


if __name__ == "__main__":
    unittest.main()
