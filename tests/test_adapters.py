"""Unit tests for Japanese, English, and Spanish Adapters."""

import unittest
from languages.ja.adapter import JapaneseAdapter
from languages.en.adapter import EnglishAdapter
from languages.es.adapter import SpanishAdapter
from core.primitives import IntentPrimitive
from core.ir_schema import CommunicationIR, IntentNode, ContentNode


class TestAdapters(unittest.TestCase):
    def setUp(self):
        self.ja_adapter = JapaneseAdapter()
        self.en_adapter = EnglishAdapter()
        self.es_adapter = SpanishAdapter()

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

    def test_spanish_condition_realization(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="CONDITION",
                condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "value": "tomorrow"}},
                consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO"}}
            )
        )
        es_text = self.es_adapter.realize(ir)
        self.assertIn("Si llueve", es_text)
        self.assertIn("no voy", es_text)

    def test_spanish_desire_and_request(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="EVENT",
                predicate="EAT",
                extra={"modality": "DESIRE"}
            )
        )
        es_text = self.es_adapter.realize(ir)
        self.assertIn("Quiero comer", es_text)

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
