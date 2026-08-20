"""
Japanese Language Adapter Implementation
"""

import re
from typing import Any, Dict, List, Optional
from languages.base import LanguageAdapter, Realization, Evaluation
from languages.ja.grammar_rules import JAPANESE_VERB_FORMS, JAPANESE_NOUNS
from languages.ja.syntax_validator import JapaneseSyntaxValidator
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
        _, parsed_ir = JapaneseSyntaxValidator.validate_and_evaluate(text)
        return parsed_ir

    def evaluate_naturalness(self, text: str, ir: CommunicationIR, context: Optional[ConversationContext] = None) -> Evaluation:
        eval_res, _ = JapaneseSyntaxValidator.validate_and_evaluate(text)
        return eval_res

    def get_realizations(self, concept: str, context: Optional[ConversationContext] = None) -> List[Realization]:
        if concept == "CONDITION":
            return [
                Realization(surface="～たら", pattern="{predicate_tara}", frequency=0.85),
                Realization(surface="～なら", pattern="{noun_nara}", frequency=0.70),
            ]
        return [Realization(surface="です", frequency=0.9)]
