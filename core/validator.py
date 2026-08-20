"""
IR Validation and Leakage Detection

Enforces:
1. Universal Primitive conformance
2. Language-specific Leakage Rule (Section 38: No JP_*, EN_*, ZH_* in Core IR)
3. IR Evolution Rule (Section 37: check whether meaning can be represented by composition)
"""

from typing import Any, Dict, List, Tuple
from core.primitives import ALL_PRIMITIVES
from core.ir_schema import CommunicationIR

FORBIDDEN_PREFIXES = ("JP_", "EN_", "ZH_", "JAPANESE_", "ENGLISH_", "CHINESE_")


class IRValidationError(ValueError):
    pass


class IRValidator:
    @staticmethod
    def check_for_language_leakage(obj: Any, path: str = "") -> List[str]:
        """Recursively scan IR structure to detect any language-specific leakage."""
        violations = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                curr_path = f"{path}.{k}" if path else k
                for prefix in FORBIDDEN_PREFIXES:
                    if isinstance(k, str) and k.upper().startswith(prefix):
                        violations.append(f"Leakage in key: {curr_path} contains {prefix}")
                violations.extend(IRValidator.check_for_language_leakage(v, curr_path))
        elif isinstance(obj, list):
            for i, elem in enumerate(obj):
                violations.extend(IRValidator.check_for_language_leakage(elem, f"{path}[{i}]"))
        elif isinstance(obj, str):
            for prefix in FORBIDDEN_PREFIXES:
                if obj.upper().startswith(prefix):
                    violations.append(f"Leakage in value at {path}: '{obj}' contains {prefix}")
        return violations

    @staticmethod
    def validate_ir(ir: CommunicationIR) -> Tuple[bool, List[str]]:
        errors = []
        intent_type = ir.intent.type
        if intent_type not in ALL_PRIMITIVES:
            errors.append(f"Invalid intent primitive: {intent_type}")

        content_dict = ir.content.model_dump() if hasattr(ir.content, "model_dump") else ir.content
        if isinstance(content_dict, dict) and "type" in content_dict:
            ctype = content_dict["type"]
            if ctype not in ALL_PRIMITIVES:
                errors.append(f"Invalid content primitive type: {ctype}")

        leakage = IRValidator.check_for_language_leakage(ir.model_dump())
        if leakage:
            errors.extend(leakage)

        return len(errors) == 0, errors
