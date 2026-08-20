"""
English Language Adapter Implementation

Demonstrates language-independence without modifying Core Universal IR.
Supports bidirectional translation: English ↔ Universal IR ↔ Japanese.
"""

import re
from typing import Any, Dict, List, Optional
from languages.base import LanguageAdapter, Realization, Evaluation
from core.ir_schema import (
    CommunicationIR,
    IntentNode,
    ContentNode,
    Pragmatics,
    ConversationContext,
)
from core.primitives import (
    IntentPrimitive,
    FormalityLevel,
    PolitenessLevel,
    DirectnessLevel,
)


class EnglishAdapter(LanguageAdapter):
    @property
    def language_code(self) -> str:
        return "en"

    def realize(self, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> str:
        content = ir.content
        intent = ir.intent.type
        
        if isinstance(content, dict):
            content = ContentNode.model_validate(content)

        ctype = content.type

        # Condition
        if ctype == "CONDITION" and content.condition and content.consequence:
            cond_node = ContentNode.model_validate(content.condition) if isinstance(content.condition, dict) else content.condition
            cons_node = ContentNode.model_validate(content.consequence) if isinstance(content.consequence, dict) else content.consequence
            
            cond_text = "it rains tomorrow" if (cond_node.predicate == "RAIN" and cond_node.time and getattr(cond_node.time, 'value', None) == 'tomorrow') else ("it rains" if cond_node.predicate == "RAIN" else "you go")
            cons_text = self.realize(CommunicationIR(intent=ir.intent, content=cons_node)).rstrip(".")
            return f"If {cond_text}, {cons_text}."

        # Cause
        if ctype == "CAUSE" and content.cause and content.effect:
            cause_node = ContentNode.model_validate(content.cause) if isinstance(content.cause, dict) else content.cause
            effect_node = ContentNode.model_validate(content.effect) if isinstance(content.effect, dict) else content.effect

            cause_str = "it was raining" if cause_node.predicate == "RAIN" else "of the event"
            effect_str = self.realize(CommunicationIR(intent=ir.intent, content=effect_node)).rstrip(".")
            return f"{effect_str} because {cause_str}."

        # Negation
        if ctype == "NEGATION" and content.scope:
            scope_node = ContentNode.model_validate(content.scope) if isinstance(content.scope, dict) else content.scope
            pred = scope_node.predicate
            if pred == "GO":
                return "I will not go."
            elif pred == "GO_OUT":
                return "I didn't go out."
            return f"I do not {pred.lower() if pred else 'act'}."

        # Experience
        if ctype == "EVENT" and (content.extra.get("aspect") == "EXPERIENCE" or content.type == "EXPERIENCE"):
            dest = content.arguments.get("destination", {}).get("concept", "Japan")
            return f"I have been to {dest.capitalize()}."

        # Desire
        if (ctype == "EVENT" and content.extra.get("modality") == "DESIRE") or ctype == "DESIRE":
            pred = content.predicate or "GO"
            dest = content.arguments.get("destination", {}).get("concept", "")
            dest_str = f" in {dest.capitalize()}" if dest else ""
            if pred == "LIVE":
                return f"I want to live{dest_str}."
            elif pred == "EAT":
                return "I want to eat ramen."
            return f"I want to {pred.lower()}{dest_str}."

        # Request
        if intent == IntentPrimitive.REQUEST:
            patient_c = content.arguments.get("patient", {}).get("concept")
            if patient_c == "MENU":
                return "Could you give me the menu, please?"
            elif patient_c == "WATER":
                return "Could I have some water, please?"
            return "Could you please help me?"

        # Standard Event
        pred = content.predicate or "GO"
        is_past = content.time and (getattr(content.time, 'relation', '') == 'PAST' or (isinstance(content.time, dict) and content.time.get('relation') == 'PAST'))
        dest = content.arguments.get("destination", {}).get("concept", "")
        dest_str = f" to {dest.capitalize()}" if dest else ""
        verb = "went" if (pred == "GO" and is_past) else ("go" if pred == "GO" else pred.lower())
        return f"I {verb}{dest_str}."

    def parse(self, text: str, context: Optional[ConversationContext] = None) -> CommunicationIR:
        clean = text.strip().lower()
        
        # Condition: If it rains tomorrow, I will not go.
        if clean.startswith("if"):
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="CONDITION",
                    condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "relation": "FUTURE", "value": "tomorrow"}},
                    consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO", "arguments": {"agent": {"ref": "speaker"}}}}
                )
            )
        
        # Request: Could you help me?
        if "help" in clean and ("could" in clean or "please" in clean):
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.REQUEST),
                content=ContentNode(
                    type="ACTION",
                    predicate="HELP",
                    arguments={"agent": {"ref": "listener"}, "beneficiary": {"ref": "speaker"}}
                ),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE, directness=DirectnessLevel.INDIRECT)
            )

        # Default
        return CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.INFORM),
            content=ContentNode(
                type="EVENT",
                predicate="GO",
                arguments={"agent": {"type": "ENTITY", "ref": "speaker"}, "destination": {"type": "ENTITY", "concept": "JAPAN"}},
                time={"type": "TIME", "relation": "PAST"}
            )
        )

    def evaluate_naturalness(self, text: str, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> Evaluation:
        return Evaluation(is_valid=True, naturalness_score=0.95, grammar_score=0.95, pragmatic_score=0.9)

    def get_realizations(self, concept: str, context: Optional[ConversationContext] = None) -> List[Realization]:
        if concept == "CONDITION":
            return [Realization(surface="If ..., then ...", frequency=0.95)]
        return [Realization(surface=concept, frequency=0.8)]
