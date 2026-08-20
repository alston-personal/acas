"""Unit tests for Universal Communication IR Schema & Validation."""

import unittest
from core.primitives import IntentPrimitive, SemanticPrimitive, LogicPrimitive
from core.ir_schema import CommunicationIR, IntentNode, ContentNode, Pragmatics
from core.validator import IRValidator


class TestIRSchema(unittest.TestCase):
    def test_basic_event_ir(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="EVENT",
                predicate="GO",
                arguments={"agent": {"type": "ENTITY", "ref": "speaker"}, "destination": {"type": "ENTITY", "concept": "JAPAN"}},
                time={"type": "TIME", "relation": "PAST"}
            )
        )
        json_str = ir.to_json()
        self.assertIn("INFORM", json_str)
        self.assertIn("JAPAN", json_str)
        
        valid, errors = IRValidator.validate_ir(ir)
        self.assertTrue(valid, f"Validation failed: {errors}")

    def test_condition_ir(self):
        ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="CONDITION",
                condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "relation": "FUTURE", "value": "tomorrow"}},
                consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO", "arguments": {"agent": {"ref": "speaker"}}}}
            )
        )
        valid, errors = IRValidator.validate_ir(ir)
        self.assertTrue(valid)

    def test_language_leakage_detection(self):
        bad_dict = {
            "ir_version": "0.1",
            "type": "utterance",
            "intent": {"type": "INFORM"},
            "content": {"type": "EVENT", "JP_GRAMMAR": "TARA"},
        }
        violations = IRValidator.check_for_language_leakage(bad_dict)
        self.assertTrue(len(violations) > 0)
        self.assertIn("JP_", violations[0])


if __name__ == "__main__":
    unittest.main()
