"""
ACAS Universal Communication IR Primitives v0.1

Defines ~50 core universal primitives spanning 6 categories:
1. Semantic
2. Logic
3. Epistemic / Mental State
4. Communicative Intent
5. Conversation Control
6. Pragmatics

RULE: NO language-specific tokens allowed in this file.
"""

from enum import Enum
from typing import Set


class SemanticPrimitive(str, Enum):
    ENTITY = "ENTITY"
    ACTION = "ACTION"
    STATE = "STATE"
    EVENT = "EVENT"
    PROPERTY = "PROPERTY"
    LOCATION = "LOCATION"
    TIME = "TIME"
    QUANTITY = "QUANTITY"
    POSSESSION = "POSSESSION"
    RELATION = "RELATION"


class LogicPrimitive(str, Enum):
    NEGATION = "NEGATION"
    CAUSE = "CAUSE"
    RESULT = "RESULT"
    CONDITION = "CONDITION"
    CONTRAST = "CONTRAST"
    COMPARISON = "COMPARISON"
    ALTERNATIVE = "ALTERNATIVE"
    SEQUENCE = "SEQUENCE"
    INCLUSION = "INCLUSION"
    EXCLUSION = "EXCLUSION"


class EpistemicPrimitive(str, Enum):
    KNOW = "KNOW"
    THINK = "THINK"
    BELIEVE = "BELIEVE"
    DOUBT = "DOUBT"
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"
    CERTAIN = "CERTAIN"
    REMEMBER = "REMEMBER"
    FORGET = "FORGET"
    EXPECT = "EXPECT"


class IntentPrimitive(str, Enum):
    INFORM = "INFORM"
    ASK = "ASK"
    ANSWER = "ANSWER"
    REQUEST = "REQUEST"
    COMMAND = "COMMAND"
    SUGGEST = "SUGGEST"
    INVITE = "INVITE"
    OFFER = "OFFER"
    PROMISE = "PROMISE"
    WARN = "WARN"
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"
    REFUSE = "REFUSE"


class ControlPrimitive(str, Enum):
    ACKNOWLEDGE = "ACKNOWLEDGE"
    CONFIRM = "CONFIRM"
    CLARIFY = "CLARIFY"
    CORRECT = "CORRECT"
    REPAIR = "REPAIR"
    CONTINUE = "CONTINUE"
    CHANGE_TOPIC = "CHANGE_TOPIC"
    RETURN_TOPIC = "RETURN_TOPIC"


class FormalityLevel(str, Enum):
    INFORMAL = "informal"
    NEUTRAL = "neutral"
    FORMAL = "formal"
    HONORIFIC = "honorific"


class PolitenessLevel(str, Enum):
    CASUAL = "casual"
    NEUTRAL = "neutral"
    POLITE = "polite"
    DEFERENTIAL = "deferential"


class DirectnessLevel(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    HINT = "hint"


ALL_PRIMITIVES: Set[str] = set(
    [p.value for p in SemanticPrimitive]
    + [p.value for p in LogicPrimitive]
    + [p.value for p in EpistemicPrimitive]
    + [p.value for p in IntentPrimitive]
    + [p.value for p in ControlPrimitive]
)
