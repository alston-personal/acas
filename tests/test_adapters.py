"""Unit tests for Japanese & English Adapters."""

import unittest
from languages.ja.adapter import JapaneseAdapter
from languages.en.adapter import EnglishAdapter
from core.primitives import IntentPrimitive
from core.ir_schema import CommunicationIR, IntentNode, ContentNode


class TestAdapters(unittest.TestCase):
    def setUp(self):
        self.ja_adapter = JapaneseAdapter()
        self.en_adapter = EnglishAdapter()

    def test_japanese_condition_realization(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="CONDITION",
                condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "value": "tomorrow"}},
                consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO"}}
            )
        )
        ja_text = self.ja_adapter.realize(ir)
        self.assertIn("たら", ja_text)
        self.assertIn("行かない", ja_text)

    def test_english_condition_realization(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="CONDITION",
                condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "value": "tomorrow"}},
                consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO"}}
            )
        )
        en_text = self.en_adapter.realize(ir)
        self.assertIn("If it rains tomorrow", en_text)
        self.assertIn("will not go", en_text)

    def test_japanese_request_realization(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.REQUEST),
            content=ContentNode(
                type="ACTION",
                predicate="HELP",
                arguments={"agent": {"ref": "listener"}, "beneficiary": {"ref": "speaker"}}
            )
        )
        ja_text = self.ja_adapter.realize(ir)
        self.assertIn("手伝ってください", ja_text)


if __name__ == "__main__":
    unittest.main()
