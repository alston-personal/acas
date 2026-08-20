"""
Japanese Morpho-Syntactic AST Validator.
"""

import re
from typing import Dict, List, Optional, Tuple
from languages.base import Evaluation
from core.ir_schema import CommunicationIR, IntentNode, ContentNode, Pragmatics
from core.primitives import IntentPrimitive, PolitenessLevel


class JapaneseSyntaxValidator:
    @classmethod
    def validate_and_evaluate(cls, text: str, target_skills: List[str] = None) -> Tuple[Evaluation, CommunicationIR]:
        clean = text.replace(" ", "").replace("、", "").replace("。", "").strip()
        feedback = []
        detected_skills = []

        if not clean or len(clean) < 2:
            return (
                Evaluation(is_valid=False, naturalness_score=0.0, grammar_score=0.0, pragmatic_score=0.0, feedback=["輸入為空或過短"]),
                CommunicationIR(intent=IntentNode(type=IntentPrimitive.INFORM), content=ContentNode(type="EVENT", predicate="UNKNOWN"))
            )

        # 1. Dangling Conjunction 'と' check (e.g. "旅行と 好きです")
        if re.search(r'と(好き|です|ます|だ|行|食|飲|休|見|買)', clean):
            feedback.append("【語法錯誤：助詞殘缺】助詞『と』是並列連接詞，後面必須接另一個名詞或動作（例如『旅行と言語を学ぶのが』），不能直接接謂語『好きです』。")
            return (
                Evaluation(is_valid=False, naturalness_score=0.25, grammar_score=0.20, pragmatic_score=0.40, feedback=feedback),
                CommunicationIR(intent=IntentNode(type=IntentPrimitive.INFORM), content=ContentNode(type="EVENT", predicate="BROKEN_SYNTAX"))
            )

        # 2. Repeated particles
        if re.search(r'(をを|にに|がが|でで|はは|とと)', clean):
            feedback.append("【語法錯誤：助詞重複】出現了連續重複的無效助詞。")
            return (
                Evaluation(is_valid=False, naturalness_score=0.20, grammar_score=0.20, pragmatic_score=0.30, feedback=feedback),
                CommunicationIR(intent=IntentNode(type=IntentPrimitive.INFORM), content=ContentNode(type="EVENT", predicate="BROKEN_SYNTAX"))
            )

        # 3. Preference Case Frame
        if "好き" in clean:
            detected_skills.append("JP.DESIRE.PREFERENCE")
            if not ("が好き" in clean or "のが好き" in clean or "ことが好き" in clean):
                if "を好き" in clean or "に好き" in clean or "で好き" in clean:
                    feedback.append("【語法錯誤：助詞誤用】表達喜好的對象應該使用助詞『が』，而非『を/に/で』。")
                    return (
                        Evaluation(is_valid=False, naturalness_score=0.45, grammar_score=0.40, pragmatic_score=0.50, feedback=feedback),
                        CommunicationIR(intent=IntentNode(type=IntentPrimitive.INFORM), content=ContentNode(type="PREFERENCE", predicate="LIKE"))
                    )

        # 4. Condition Clause Frame
        if "たら" in clean or "なら" in clean or "ば" in clean:
            detected_skills.append("JP.CONDITION.TARA")
            if clean.endswith("たら") or clean.endswith("なら") or clean.endswith("ば"):
                feedback.append("【語法錯誤：句子殘缺】只有條件假設，缺少後續的行動或結果子句。")
                return (
                    Evaluation(is_valid=False, naturalness_score=0.40, grammar_score=0.35, pragmatic_score=0.40, feedback=feedback),
                    CommunicationIR(intent=IntentNode(type=IntentPrimitive.INFORM), content=ContentNode(type="CONDITION"))
                )

        if "たい" in clean:
            detected_skills.append("JP.DESIRE.TAI")
        if "ください" in clean:
            detected_skills.append("JP.REQUEST.KUDASAI")
        if "ことがある" in clean or "ことがあります" in clean:
            detected_skills.append("JP.EXPERIENCE.TAKOTOGAARU")
        if "です" in clean or "ます" in clean:
            detected_skills.append("JP.INFORM.DESU")

        has_valid_ending = any(clean.endswith(e) for e in [
            "です", "ます", "ません", "でした", "ませんでした", "ください", "たいです", "たい",
            "ことがあります", "ことがある", "ない", "ある", "いる", "行きます", "食べます", "お願いします", "ありがとう", "大丈夫です", "います", "会いました"
        ])

        if not has_valid_ending and len(clean) > 4:
            feedback.append("【語法未完結】句子結尾缺少完整的謂語或結尾詞。")
            grammar_score = 0.50
            naturalness_score = 0.50
            is_valid = False
        else:
            grammar_score = 0.95 if len(feedback) == 0 else 0.40
            naturalness_score = 0.92 if len(feedback) == 0 else 0.40
            is_valid = (len(feedback) == 0)

        pragmatic_score = 0.90 if ("です" in clean or "ます" in clean or "ください" in clean or "お願いします" in clean) else 0.65

        parsed_ir = CommunicationIR(
            intent=IntentNode(type=IntentPrimitive.REQUEST if "ください" in clean or "お願い" in clean else IntentPrimitive.INFORM),
            content=ContentNode(type="EVENT", predicate="INFORM"),
            pragmatics=Pragmatics(politeness=PolitenessLevel.POLITE if ("です" in clean or "ます" in clean) else PolitenessLevel.CASUAL)
        )

        return (
            Evaluation(
                is_valid=is_valid,
                naturalness_score=naturalness_score,
                grammar_score=grammar_score,
                pragmatic_score=pragmatic_score,
                detected_skills=detected_skills,
                feedback=feedback
            ),
            parsed_ir
        )
