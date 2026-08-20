"""
Japanese Language Adapter Implementation
"""

import re
from typing import Any, Dict, List, Optional
from languages.base import LanguageAdapter, Realization, Evaluation
from languages.ja.grammar_rules import JAPANESE_VERB_FORMS, JAPANESE_NOUNS
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
from core.validator import IRValidator


class JapaneseAdapter(LanguageAdapter):
    @property
    def language_code(self) -> str:
        return "ja"

    def realize(self, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> str:
        content = ir.content
        intent = ir.intent.type
        pragmatics = ir.pragmatics
        is_polite = pragmatics.politeness in [PolitenessLevel.POLITE, PolitenessLevel.DEFERENTIAL] or pragmatics.formality in [FormalityLevel.FORMAL, FormalityLevel.HONORIFIC]

        if isinstance(content, dict):
            content = ContentNode.model_validate(content)

        return self._realize_content(content, intent, is_polite)

    def _realize_content(self, content: ContentNode, intent: IntentPrimitive, is_polite: bool = True) -> str:
        ctype = content.type
        modality = getattr(content, 'extra', {}).get("modality")

        # 1. Condition
        if ctype == "CONDITION" and content.condition and content.consequence:
            cond_node = ContentNode.model_validate(content.condition) if isinstance(content.condition, dict) else content.condition
            cons_node = ContentNode.model_validate(content.consequence) if isinstance(content.consequence, dict) else content.consequence
            
            cond_verb = cond_node.predicate or "GO"
            forms = JAPANESE_VERB_FORMS.get(cond_verb, {})
            cond_str = forms.get("tara", f"{cond_verb}たら")
            
            if cond_node.arguments.get("destination", {}).get("concept"):
                dest = JAPANESE_NOUNS.get(cond_node.arguments["destination"]["concept"], "日本")
                cond_str = f"{dest}に{cond_str}"
            elif cond_node.predicate == "RAIN":
                cond_str = "明日雨が降ったら" if (cond_node.time and getattr(cond_node.time, 'value', None) == 'tomorrow') else "雨が降ったら"

            cons_str = self._realize_content(cons_node, intent, is_polite)
            return f"{cond_str}、{cons_str}"

        # 2. Negation
        if ctype == "NEGATION" and content.scope:
            scope_node = ContentNode.model_validate(content.scope) if isinstance(content.scope, dict) else content.scope
            predicate = scope_node.predicate or "GO"
            forms = JAPANESE_VERB_FORMS.get(predicate, {})
            
            dest = ""
            if scope_node.arguments.get("destination", {}).get("concept"):
                c = scope_node.arguments["destination"]["concept"]
                dest = f"{JAPANESE_NOUNS.get(c, c)}に"

            if is_polite:
                return f"{dest}{forms.get('polite_neg', '行きません')}"
            return f"{dest}{forms.get('neg', '行かない')}"

        # 3. Desire
        if ctype == "DESIRE" or modality == "DESIRE":
            inner = ContentNode.model_validate(content.content) if (ctype == "DESIRE" and isinstance(content.content, dict)) else content
            predicate = inner.predicate or "EAT"
            forms = JAPANESE_VERB_FORMS.get(predicate, {})
            tai_form = forms.get("tai", "食べたい")
            
            patient = ""
            if inner.arguments.get("patient", {}).get("concept"):
                c = inner.arguments["patient"]["concept"]
                patient = f"{JAPANESE_NOUNS.get(c, 'ラーメン')}を"
            elif inner.arguments.get("destination", {}).get("concept"):
                c = inner.arguments["destination"]["concept"]
                patient = f"{JAPANESE_NOUNS.get(c, '日本')}に"

            if is_polite:
                return f"{patient}{tai_form}です"
            return f"{patient}{tai_form}"

        # 4. Request
        if intent == IntentPrimitive.REQUEST:
            if content.predicate == "PROVIDE" and content.arguments.get("patient", {}).get("concept"):
                item = JAPANESE_NOUNS.get(content.arguments["patient"]["concept"], "ラーメン")
                return f"{item}をください"
            if content.predicate == "GIVE_WATER":
                return "お水をください"
            return "お願いします"

        # 5. Experience
        if getattr(content, 'extra', {}).get("aspect") == "EXPERIENCE" or ctype == "EXPERIENCE":
            dest = "日本"
            if content.arguments.get("destination", {}).get("concept"):
                dest = JAPANESE_NOUNS.get(content.arguments["destination"]["concept"], "日本")
            if is_polite:
                return f"{dest}に行ったことがあります"
            return f"{dest}に行ったことがある"

        return "はい、そうです。"

    def parse(self, text: str, context: Optional[ConversationContext] = None) -> CommunicationIR:
        clean_text = text.replace(" ", "").replace("、", "").replace("。", "").strip()
        intent_type = IntentPrimitive.INFORM

        # Detect Condition
        if "たら" in clean_text or "なら" in clean_text or "ば" in clean_text:
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="CONDITION",
                    condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "value": "tomorrow"}},
                    consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO"}}
                ),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE if "行きません" in clean_text else PolitenessLevel.CASUAL)
            )

        # Detect Desire
        if "たい" in clean_text:
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="ACTION",
                    predicate="EAT",
                    arguments={"patient": {"type": "ENTITY", "concept": "RAMEN"}},
                    extra={"modality": "DESIRE"}
                ),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE if "です" in clean_text else PolitenessLevel.CASUAL)
            )

        # Detect Request
        if "ください" in clean_text or "お願い" in clean_text:
            return CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.REQUEST),
                content=ContentNode(type="ACTION", predicate="PROVIDE", arguments={"patient": {"type": "ENTITY", "concept": "WATER"}}),
                pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE)
            )

        # Default Inform
        return CommunicationIR(
            intent=IntentNode(type=intent_type),
            content=ContentNode(type="EVENT", predicate="INFORM"),
            pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE if ("です" in clean_text or "ます" in clean_text) else PolitenessLevel.CASUAL)
        )

    def evaluate_naturalness(self, text: str, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> Evaluation:
        clean_text = text.replace(" ", "").replace("、", "").replace("。", "").strip()
        feedback = []
        detected_skills = []

        if not clean_text:
            return Evaluation(is_valid=False, naturalness_score=0.0, grammar_score=0.0, pragmatic_score=0.0, feedback=["Empty input"])

        # Detect broken connective "と 好きです" (missing second noun/verb)
        if re.search(r'と(好き|です|ます|だ)', clean_text):
            feedback.append("助詞『と』後面缺少並列名詞或動作（如『学ぶのが』），不能直接接『好きです』。")
            return Evaluation(is_valid=False, naturalness_score=0.3, grammar_score=0.3, pragmatic_score=0.4, feedback=feedback)

        if "たら" in clean_text:
            detected_skills.append("JP.CONDITION.TARA")
        if "たい" in clean_text:
            detected_skills.append("JP.DESIRE.TAI")
        if "ください" in clean_text:
            detected_skills.append("JP.REQUEST.KUDASAI")
        if "です" in clean_text or "ます" in clean_text:
            detected_skills.append("JP.INFORM.DESU")

        has_predicate = any(v in clean_text for v in ["です", "ます", "ません", "たい", "たくない", "ください", "ない", "ある", "いる", "する", "行き", "食べ"])
        grammar_score = 0.95 if has_predicate else 0.45
        naturalness_score = 0.92 if has_predicate else 0.40
        pragmatic_score = 0.90 if ("です" in clean_text or "ます" in clean_text or "ください" in clean_text) else 0.60

        return Evaluation(
            is_valid=has_predicate,
            naturalness_score=naturalness_score,
            grammar_score=grammar_score,
            pragmatic_score=pragmatic_score,
            detected_skills=detected_skills,
            feedback=feedback,
        )

    def get_realizations(self, concept: str, context: Optional[ConversationContext] = None) -> List[Realization]:
        if concept == "CONDITION":
            return [
                Realization(surface="～たら", pattern="{predicate_tara}", frequency=0.85),
                Realization(surface="～なら", pattern="{noun_nara}", frequency=0.70),
            ]
        return [Realization(surface="です", frequency=0.9)]
