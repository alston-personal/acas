"""
Universal Concept Lexicon Registry

Decouples concepts (e.g. FOOD.APPLE, ACTION.EAT) from natural language realization (Section 29).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LexicalRealization(BaseModel):
    surface: str
    reading: Optional[str] = None
    register: str = "neutral"
    part_of_speech: Optional[str] = None


class ConceptDefinition(BaseModel):
    concept_id: str
    category: str
    communication_utility: float = Field(default=0.8, ge=0.0, le=1.0)
    scenario_coverage: float = Field(default=0.8, ge=0.0, le=1.0)
    realizations: Dict[str, List[Any]] = Field(default_factory=dict)


class VocabularyRegistry:
    def __init__(self):
        self._concepts: Dict[str, ConceptDefinition] = {}
        self._init_default_lexicon()

    def register(self, concept: ConceptDefinition):
        self._concepts[concept.concept_id] = concept

    def get(self, concept_id: str) -> Optional[ConceptDefinition]:
        return self._concepts.get(concept_id)

    def calculate_priority(self, concept_id: str, personal_relevance: float = 1.0, compositional_utility: float = 1.0) -> float:
        c = self.get(concept_id)
        if not c:
            return 0.0
        return c.communication_utility * c.scenario_coverage * personal_relevance * compositional_utility

    def _init_default_lexicon(self):
        defaults = [
            ConceptDefinition(
                concept_id="FOOD.RAMEN",
                category="food",
                communication_utility=0.9,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["拉麵"],
                    "en": ["ramen", "ramen noodles"],
                    "ja": [{"surface": "ラーメン", "reading": "らーめん"}],
                },
            ),
            ConceptDefinition(
                concept_id="FOOD.APPLE",
                category="food",
                communication_utility=0.7,
                scenario_coverage=0.6,
                realizations={
                    "zh": ["蘋果"],
                    "en": ["apple"],
                    "ja": [{"surface": "りんご", "reading": "りんご"}],
                },
            ),
            ConceptDefinition(
                concept_id="FOOD.WATER",
                category="drink",
                communication_utility=0.95,
                scenario_coverage=0.95,
                realizations={
                    "zh": ["水", "開水"],
                    "en": ["water"],
                    "ja": [{"surface": "お水", "reading": "おみず"}, {"surface": "水", "reading": "みず"}],
                },
            ),
            ConceptDefinition(
                concept_id="FOOD.MENU",
                category="restaurant",
                communication_utility=0.95,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["菜單"],
                    "en": ["menu"],
                    "ja": [{"surface": "メニュー", "reading": "めにゅー"}],
                },
            ),
            ConceptDefinition(
                concept_id="ACTION.EAT",
                category="action",
                communication_utility=0.95,
                scenario_coverage=0.95,
                realizations={
                    "zh": ["吃"],
                    "en": ["eat"],
                    "ja": [{"surface": "食べる", "reading": "たべる"}],
                },
            ),
            ConceptDefinition(
                concept_id="ACTION.DRINK",
                category="action",
                communication_utility=0.9,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["喝"],
                    "en": ["drink"],
                    "ja": [{"surface": "飲む", "reading": "のむ"}],
                },
            ),
            ConceptDefinition(
                concept_id="ACTION.GO",
                category="action",
                communication_utility=0.98,
                scenario_coverage=0.95,
                realizations={
                    "zh": ["去", "前往"],
                    "en": ["go"],
                    "ja": [{"surface": "行く", "reading": "いく"}],
                },
            ),
            ConceptDefinition(
                concept_id="ACTION.COME",
                category="action",
                communication_utility=0.95,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["來"],
                    "en": ["come"],
                    "ja": [{"surface": "来る", "reading": "くる"}],
                },
            ),
            ConceptDefinition(
                concept_id="ACTION.BUY",
                category="action",
                communication_utility=0.92,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["買"],
                    "en": ["buy", "purchase"],
                    "ja": [{"surface": "買う", "reading": "かう"}],
                },
            ),
            ConceptDefinition(
                concept_id="ACTION.HELP",
                category="action",
                communication_utility=0.9,
                scenario_coverage=0.85,
                realizations={
                    "zh": ["幫忙", "協助"],
                    "en": ["help", "assist"],
                    "ja": [{"surface": "手伝う", "reading": "てつだう"}, {"surface": "助ける", "reading": "たすける"}],
                },
            ),
            ConceptDefinition(
                concept_id="LOCATION.JAPAN",
                category="location",
                communication_utility=0.9,
                scenario_coverage=0.85,
                realizations={
                    "zh": ["日本"],
                    "en": ["Japan"],
                    "ja": [{"surface": "日本", "reading": "にほん"}],
                },
            ),
            ConceptDefinition(
                concept_id="LOCATION.TOKYO",
                category="location",
                communication_utility=0.9,
                scenario_coverage=0.8,
                realizations={
                    "zh": ["東京"],
                    "en": ["Tokyo"],
                    "ja": [{"surface": "東京", "reading": "とうきょう"}],
                },
            ),
            ConceptDefinition(
                concept_id="LOCATION.HOTEL",
                category="location",
                communication_utility=0.92,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["飯店", "酒店"],
                    "en": ["hotel"],
                    "ja": [{"surface": "ホテル", "reading": "ほてる"}],
                },
            ),
            ConceptDefinition(
                concept_id="LOCATION.STATION",
                category="location",
                communication_utility=0.95,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["車站"],
                    "en": ["station", "train station"],
                    "ja": [{"surface": "駅", "reading": "えき"}],
                },
            ),
            ConceptDefinition(
                concept_id="WEATHER.RAIN",
                category="weather",
                communication_utility=0.85,
                scenario_coverage=0.8,
                realizations={
                    "zh": ["下雨"],
                    "en": ["rain", "raining"],
                    "ja": [{"surface": "雨", "reading": "あめ"}],
                },
            ),
            ConceptDefinition(
                concept_id="TIME.TOMORROW",
                category="time",
                communication_utility=0.95,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["明天"],
                    "en": ["tomorrow"],
                    "ja": [{"surface": "明日", "reading": "あした"}],
                },
            ),
            ConceptDefinition(
                concept_id="TIME.TODAY",
                category="time",
                communication_utility=0.95,
                scenario_coverage=0.9,
                realizations={
                    "zh": ["今天"],
                    "en": ["today"],
                    "ja": [{"surface": "今日", "reading": "きょう"}],
                },
            ),
        ]
        for item in defaults:
            self.register(item)


global_vocab = VocabularyRegistry()
