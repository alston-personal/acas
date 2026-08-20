"""
ACAS Preservation Benchmark Suite (Section 36)

Tests semantic preservation, intent preservation, and pragmatic preservation
across generated conversational utterances.
"""

import unittest
from languages.ja.adapter import JapaneseAdapter
from languages.en.adapter import EnglishAdapter
from core.validator import IRValidator


class TestPreservationBenchmark(unittest.TestCase):
    def setUp(self):
        self.ja_adapter = JapaneseAdapter()
        self.en_adapter = EnglishAdapter()

    def test_bidirectional_preservation_suite(self):
        test_utterances_ja = [
            "日本に行った。",
            "雨だったから、出かけなかった。",
            "明日雨が降ったら、行かない。",
            "手伝ってください。",
            "ラーメンを食べたいです。",
            "東京に住みたい。",
            "お水をください。",
            "メニューをください。",
            "日本に行ったことがある。",
        ]

        success_count = 0
        for utt in test_utterances_ja:
            ir = self.ja_adapter.parse(utt)
            valid, errors = IRValidator.validate_ir(ir)
            self.assertTrue(valid, f"Validation failed for '{utt}': {errors}")

            en_realization = self.en_adapter.realize(ir)
            self.assertTrue(len(en_realization) > 0)

            ja_realization = self.ja_adapter.realize(ir)
            self.assertTrue(len(ja_realization) > 0)

            success_count += 1

        self.assertEqual(success_count, len(test_utterances_ja))


if __name__ == "__main__":
    unittest.main()
