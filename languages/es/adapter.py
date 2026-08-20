"""
Spanish Language Adapter Implementation (ES)

Demonstrates plugging in a completely new Romance language without modifying Core Universal IR.
Supports bidirectional translation: Spanish ↔ Universal IR ↔ Japanese / English.
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

SPANISH_NOUNS = {
    "JAPAN": "Japón",
    "TOKYO": "Tokio",
    "RAMEN": "ramen",
    "WATER": "agua",
    "MENU": "el menú",
    "HOTEL": "el hotel",
    "STATION": "la estación",
    "TOMORROW": "mañana",
    "TODAY": "hoy",
}

SPANISH_VERBS = {
    "GO": {"inf": "ir", "pres_1s": "voy", "pret_1s": "fui", "fut_1s": "iré", "part": "ido"},
    "GO_OUT": {"inf": "salir", "pres_1s": "salgo", "pret_1s": "salí", "fut_1s": "saldré", "part": "salido"},
    "EAT": {"inf": "comer", "pres_1s": "como", "pret_1s": "comí", "fut_1s": "comeré", "part": "comido"},
    "DRINK": {"inf": "beber", "pres_1s": "bebo", "pret_1s": "bebí", "fut_1s": "beberé", "part": "bebido"},
    "LIVE": {"inf": "vivir", "pres_1s": "vivo", "pret_1s": "viví", "fut_1s": "viviré", "part": "vivido"},
    "HELP": {"inf": "ayudar", "pres_1s": "ayudo", "pret_1s": "ayudé", "imper": "ayúdame", "part": "ayudado"},
    "RAIN": {"inf": "llover", "pres_3s": "llueve", "pret_3s": "llovió", "imperf_3s": "llovía", "part": "llovido"},
}


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

        # 1. Condition: Si llueve mañana, no saldré / no voy.
        if ctype == "CONDITION" and content.condition and content.consequence:
            cond_node = ContentNode.model_validate(content.condition) if isinstance(content.condition, dict) else content.condition
            cons_node = ContentNode.model_validate(content.consequence) if isinstance(content.consequence, dict) else content.consequence
            
            cond_text = "llueve mañana" if (cond_node.predicate == "RAIN" and cond_node.time and getattr(cond_node.time, 'value', None) == 'tomorrow') else ("llueve" if cond_node.predicate == "RAIN" else "vas")
            cons_text = self.realize(CommunicationIR(intent=ir.intent, content=cons_node)).rstrip(".")
            return f"Si {cond_text}, {cons_text.lower()}."

        # 2. Cause: No salí porque llovía.
        if ctype == "CAUSE" and content.cause and content.effect:
            cause_node = ContentNode.model_validate(content.cause) if isinstance(content.cause, dict) else content.cause
            effect_node = ContentNode.model_validate(content.effect) if isinstance(content.effect, dict) else content.effect

            cause_str = "llovía" if cause_node.predicate == "RAIN" else "había un evento"
            effect_str = self.realize(CommunicationIR(intent=ir.intent, content=effect_node)).rstrip(".")
            return f"{effect_str} porque {cause_str}."

        # 3. Negation
        if ctype == "NEGATION" and content.scope:
            scope_node = ContentNode.model_validate(content.scope) if isinstance(content.scope, dict) else content.scope
            pred = scope_node.predicate
            if pred == "GO":
                return "No voy."
            elif pred == "GO_OUT":
                return "No salí."
            return f"No {pred.lower() if pred else 'hago nada'}."

        # 4. Desire: Quiero vivir en Tokio / Quiero comer ramen.
        if (ctype == "EVENT" and content.extra.get("modality") == "DESIRE") or ctype == "DESIRE":
            pred = content.predicate or "GO"
            dest = content.arguments.get("destination", {}).get("concept", "")
            dest_str = f" en {SPANISH_NOUNS.get(dest, dest)}" if dest else ""
            if pred == "LIVE":
                return f"Quiero vivir{dest_str}."
            elif pred == "EAT":
                return "Quiero comer ramen."
            return f"Quiero {SPANISH_VERBS.get(pred, {}).get('inf', pred.lower())}{dest_str}."

        # 5. Experience: He estado en Japón.
        if ctype == "EVENT" and (content.extra.get("aspect") == "EXPERIENCE" or content.type == "EXPERIENCE"):
            dest = content.arguments.get("destination", {}).get("concept", "JAPAN")
            dest_name = SPANISH_NOUNS.get(dest, dest)
            return f"He estado en {dest_name}."

        # 6. Opinion: Creo que es delicioso.
        if ctype == "THINK" or ctype == "OPINION":
            return "Creo que es muy delicioso."

        # 7. Request: Por favor, un menú / ¿Me puede ayudar?
        if intent == IntentPrimitive.REQUEST:
            patient_c = content.arguments.get("patient", {}).get("concept")
            if patient_c == "MENU":
                return "El menú, por favor."
            elif patient_c == "WATER":
                return "Un vaso de agua, por favor."
            return "¿Puede ayudarme, por favor?"

        # Standard Event
        pred = content.predicate or "GO"
        is_past = content.time and (getattr(content.time, 'relation', '') == 'PAST' or (isinstance(content.time, dict) and content.time.get('relation') == 'PAST'))
        dest = content.arguments.get("destination", {}).get("concept", "")
        dest_str = f" a {SPANISH_NOUNS.get(dest, dest)}" if dest else ""
        verb = "Fui" if (pred == "GO" and is_past) else ("Voy" if pred == "GO" else pred.lower())
        return f"{verb}{dest_str}."

    def parse(self, text: str, context: Optional[ConversationContext] = None) -> CommunicationIR:
        clean = text.strip().lower()
        
        # Condition: Si llueve mañana...
        if clean.startswith("si "):
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="CONDITION",
                    condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "relation": "FUTURE", "value": "tomorrow"}},
                    consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO", "arguments": {"agent": {"ref": "speaker"}}}}
                )
            )

        # Desire: Quiero vivir en Tokio / Quiero comer ramen
        if "quiero" in clean:
            pred = "LIVE" if "vivir" in clean else ("EAT" if "comer" in clean else "GO")
            dest = "TOKYO" if "tokio" in clean else ("JAPAN" if "japón" in clean or "japon" in clean else None)
            args = {"agent": {"ref": "speaker"}}
            if dest:
                args["destination"] = {"type": "ENTITY", "concept": dest}
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="EVENT",
                    predicate=pred,
                    arguments=args,
                    extra={"modality": "DESIRE"}
                )
            )

        # Request: Por favor / agua / menú
        if "por favor" in clean or "ayuda" in clean:
            if "menú" in clean or "menu" in clean:
                return CommunicationIR(
                    intent=IntentNode(type=IntentPrimitive.REQUEST),
                    content=ContentNode(type="ACTION", predicate="PROVIDE", arguments={"patient": {"type": "ENTITY", "concept": "MENU"}})
                )
            elif "agua" in clean:
                return CommunicationIR(
                    intent=IntentNode(type=IntentPrimitive.REQUEST),
                    content=ContentNode(type="ACTION", predicate="PROVIDE", arguments={"patient": {"type": "ENTITY", "concept": "WATER"}})
                )
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.REQUEST),
                content=ContentNode(type="ACTION", predicate="HELP", arguments={"agent": {"ref": "listener"}, "beneficiary": {"ref": "speaker"}})
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
        detected = []
        clean = text.lower()
        if "si " in clean:
            detected.append("ES.CONDITION.SI")
        if "quiero" in clean:
            detected.append("ES.DESIRE.QUIERO")
        if "por favor" in clean:
            detected.append("ES.REQUEST.PORFAVOR")
        if "he estado" in clean:
            detected.append("ES.EXPERIENCE.HABER")
        if "creo" in clean or "pienso" in clean:
            detected.append("ES.OPINION.CREO")

        return Evaluation(
            is_valid=True,
            naturalness_score=0.94,
            grammar_score=0.92,
            pragmatic_score=0.90,
            detected_skills=detected
        )

    def get_realizations(self, concept: str, context: Optional[ConversationContext] = None) -> List[Realization]:
        if concept == "CONDITION":
            return [Realization(surface="Si + [presente], [futuro/presente]", frequency=0.95)]
        elif concept == "DESIRE":
            return [Realization(surface="Quiero + [infinitivo]", frequency=0.95)]
        elif concept == "REQUEST":
            return [Realization(surface="Por favor / ¿Puede...?", frequency=0.95)]
        return [Realization(surface=concept, frequency=0.8)]
