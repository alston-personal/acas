"""Integration test for the full closed learning loop."""

import unittest
from engine.session import ACASSessionEngine


class TestClosedLoop(unittest.TestCase):
    def test_multi_turn_learning_session(self):
        engine = ACASSessionEngine(learner_id="test_learner_001")
        
        prompt1 = engine.start_next_turn()
        self.assertIsNotNone(prompt1.prompt_text_ja)
        self.assertTrue(len(prompt1.target_skills) > 0)

        result1 = engine.process_response(
            response_text="明日雨が降ったら、東京に行きません。",
            latency_ms=1400.0
        )
        self.assertGreater(result1.grammar_accuracy, 0.8)
        self.assertGreater(result1.semantic_correctness, 0.8)

        progress1 = engine.compute_progress()
        self.assertGreater(progress1.dimensions.production, 0.0)

        prompt2 = engine.start_next_turn()
        self.assertIsNotNone(prompt2.prompt_text_ja)

        result2 = engine.process_response(
            response_text="ラーメンを食べたいです。",
            latency_ms=1100.0
        )
        self.assertGreater(result2.grammar_accuracy, 0.8)

        progress2 = engine.compute_progress()
        self.assertGreaterEqual(progress2.overall, progress1.overall)


if __name__ == "__main__":
    unittest.main()
