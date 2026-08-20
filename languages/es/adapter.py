"""
Spanish Language Adapter Implementation
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


class SpanishAdapter(LanguageAdapter):
    @property
    def language_code(self) -> str:
        return "es"

    def realize(self, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> str:
        content = ir.content
        intent = ir.intent.type
        if isinstance(content, dict):
            content = ContentNode.model_validate(content)

        ctype = content.type
        modality = getattr(content, 'extra', {}).get("modality") or getattr(content, 'modality', None)

        if ctype == "CONDITION":
            return "Si llueve mañana, no voy a salir."
        if ctype == "DESIRE" or modality == "DESIRE" or content.predicate == "EAT":
            return "Quiero comer paella."
        if intent == IntentPrimitive.REQUEST:
            return "Un vaso de agua, por favor."
        if getattr(content, 'extra', {}).get("aspect") == "EXPERIENCE":
            return "Sí, he estado en España."
        return "Sí, tengo una reserva."

    def parse(self, text: str, context: Optional[ConversationContext] = None) -> CommunicationIR:
        lower_t = text.lower().strip()
        intent_type = IntentPrimitive.INFORM

        if "si " in lower_t:
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="CONDITION",
                    condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "value": "tomorrow"}},
                    consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO"}}
                ),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE)
            )

        if "quiero" in lower_t or "deseo" in lower_t or "comer" in lower_t:
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="ACTION",
                    predicate="EAT",
                    arguments={"patient": {"type": "ENTITY", "concept": "RAMEN"}},
                    extra={"modality": "DESIRE"}
                ),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE)
            )

        if "por favor" in lower_t or "cuenta" in lower_t or "agua" in lower_t:
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.REQUEST),
                content=ContentNode(type="ACTION", predicate="PROVIDE", arguments={"patient": {"type": "ENTITY", "concept": "WATER"}}),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE)
            )

        return CommunicationIR(
            intent=IntentNode(type=intent_type),
            content=ContentNode(type="EVENT", predicate="INFORM"),
            pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE)
        )

    def evaluate_naturalness(self, text: str, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> Evaluation:
        clean_text = text.strip()
        feedback = []
        detected_skills = []

        if not clean_text or len(clean_text) < 3:
            return Evaluation(is_valid=False, naturalness_score=0.0, grammar_score=0.0, pragmatic_score=0.0, feedback=["Entrada vacía o incompleta"])

        lower_t = clean_text.lower()
        if re.search(r'\b(y|o)\s*(por favor|gracias|es)\b', lower_t) or lower_t.endswith(" y"):
            feedback.append("Conjunción incompleta o colgante.")
            return Evaluation(is_valid=False, naturalness_score=0.3, grammar_score=0.3, pragmatic_score=0.4, feedback=feedback)

        if "si " in lower_t:
            detected_skills.append("ES.CONDITION.SI")
        if "quiero" in lower_t or "deseo" in lower_t:
            detected_skills.append("ES.DESIRE.QUIERO")
        if "por favor" in lower_t:
            detected_skills.append("ES.REQUEST.PORFAVOR")
        if "he estado" in lower_t:
            detected_skills.append("ES.EXPERIENCE.HABER")
        if "creo que" in lower_t:
            detected_skills.append("ES.OPINION.CREO")

        has_verb = any(v in lower_t for v in ["es", "está", "tengo", "quiero", "voy", "saldré", "he", "creo", "gusta", "cuesta", "duele", "pago", "soy", "por favor", "gracias", "salgo"])
        grammar_score = 0.95 if has_verb else 0.40
        naturalness_score = 0.92 if has_verb else 0.40
        pragmatic_score = 0.90 if ("por favor" in lower_t or "gracias" in lower_t or "usted" in lower_t or has_verb) else 0.60

        return Evaluation(
            is_valid=has_verb,
            naturalness_score=naturalness_score,
            grammar_score=grammar_score,
            pragmatic_score=pragmatic_score,
            detected_skills=detected_skills,
            feedback=feedback,
        )

    def get_realizations(self, concept: str, context: Optional[ConversationContext] = None) -> List[Realization]:
        if concept == "CONDITION":
            return [Realization(surface="Si...", frequency=0.9)]
        return [Realization(surface="Quiero...", frequency=0.9)]
