"""
Scenario Registry with 5+ Rich Conversational Scenarios

Covers travel, dining, hotels, daily weather, opinions, and directions.
"""

from typing import Dict, List, Optional
from scenarios.definitions import ScenarioDefinition, ScenarioTurnTemplate


class ScenarioRegistry:
    def __init__(self):
        self._scenarios: Dict[str, ScenarioDefinition] = {}
        self._init_mvp_scenarios()

    def register(self, scenario: ScenarioDefinition):
        self._scenarios[scenario.scenario_id] = scenario

    def get(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        return self._scenarios.get(scenario_id)

    def get_all(self) -> List[ScenarioDefinition]:
        return list(self._scenarios.values())

    def find_best_scenario_for_skills(self, target_skills: List[str], domain: Optional[str] = None) -> Optional[ScenarioDefinition]:
        best_scenario = None
        best_overlap = -1

        for scenario in self._scenarios.values():
            if domain and scenario.domain != domain:
                continue
            overlap = len(set(target_skills).intersection(scenario.language_skills + scenario.required_skills))
            if overlap > best_overlap:
                best_overlap = overlap
                best_scenario = scenario

        return best_scenario or (self.get_all()[0] if self.get_all() else None)

    def _init_mvp_scenarios(self):
        scenarios = [
            # 1. Travel Restaurant Order
            ScenarioDefinition(
                scenario_id="travel.restaurant.order",
                domain="travel",
                title="Restaurant Ordering & Requests",
                description="Order dishes and ask the waiter for assistance/menu politely.",
                required_skills=["CORE.REQUEST", "CORE.DESIRE", "CORE.INFORM"],
                language_skills=["JP.REQUEST.KUDASAI", "JP.DESIRE.TAI", "JP.INFORM.DESU"],
                vocabulary_domains=["food", "restaurant"],
                difficulty=0.20,
                turns=[
                    ScenarioTurnTemplate(
                        turn_id=1,
                        ai_prompt_text_ja="いらっしゃいませ！何をご注文されますか？",
                        ai_prompt_text_en="Welcome! What would you like to order?",
                        target_skills=["JP.REQUEST.KUDASAI", "JP.DESIRE.TAI"],
                        expected_ir_pattern={"predicate": "PROVIDE", "intent": "REQUEST"},
                        hints="Try asking for the menu or ramen politely (e.g. ラーメンをください / ラーメンが食べたいです)",
                    ),
                    ScenarioTurnTemplate(
                        turn_id=2,
                        ai_prompt_text_ja="かしこまりました。お飲み物はいかがですか？",
                        ai_prompt_text_en="Certainly. Would you like anything to drink?",
                        target_skills=["JP.REQUEST.KUDASAI"],
                        expected_ir_pattern={"predicate": "PROVIDE", "concept": "WATER"},
                        hints="Ask for water (e.g. お水をください)",
                    ),
                ],
            ),
            # 2. Daily Weather & Conditional Plans (Testing CONDITION & CAUSE)
            ScenarioDefinition(
                scenario_id="daily.weather.plan",
                domain="daily_life",
                title="Weather & Weekend Plans",
                description="Discuss conditional plans depending on the weather.",
                required_skills=["CORE.CONDITION", "CORE.CAUSE", "CORE.NEGATION"],
                language_skills=["JP.CONDITION.TARA", "JP.CONDITION.NARA", "JP.CAUSE.KARA", "JP.NEGATION.NAI"],
                vocabulary_domains=["weather", "time", "action"],
                difficulty=0.45,
                turns=[
                    ScenarioTurnTemplate(
                        turn_id=1,
                        ai_prompt_text_ja="明日雨が降ったら、どうしますか？",
                        ai_prompt_text_en="If it rains tomorrow, what will you do?",
                        target_skills=["JP.CONDITION.TARA", "JP.NEGATION.NAI"],
                        expected_ir_pattern={"type": "CONDITION", "predicate": "RAIN"},
                        hints="Express condition and negation (e.g. 雨が降ったら、出かけない / 行かない)",
                    ),
                    ScenarioTurnTemplate(
                        turn_id=2,
                        ai_prompt_text_ja="日本に住むなら、どこに住みたいですか？",
                        ai_prompt_text_en="If you were to live in Japan, where would you want to live?",
                        target_skills=["JP.CONDITION.NARA", "JP.DESIRE.TAI"],
                        expected_ir_pattern={"predicate": "LIVE", "concept": "TOKYO"},
                        hints="Express topical condition and desire (e.g. 東京に住みたいです)",
                    ),
                ],
            ),
            # 3. Travel Hotel Check-in & Inquiries
            ScenarioDefinition(
                scenario_id="travel.hotel.checkin",
                domain="travel",
                title="Hotel Check-in and Facilities",
                description="Check into a hotel, ask about amenities and assistance.",
                required_skills=["CORE.REQUEST", "CORE.ASK", "CORE.CONFIRM"],
                language_skills=["JP.REQUEST.KUDASAI", "JP.ASK.KA", "JP.INFORM.DESU"],
                vocabulary_domains=["hotel", "travel"],
                difficulty=0.30,
                turns=[
                    ScenarioTurnTemplate(
                        turn_id=1,
                        ai_prompt_text_ja="ご宿泊の予約確認をお願いします。お名前を教えていただけますか？",
                        ai_prompt_text_en="May I have your name for the reservation confirmation?",
                        target_skills=["JP.INFORM.DESU"],
                        expected_ir_pattern={"intent": "INFORM"},
                        hints="State your name politely (e.g. 田中です)",
                    ),
                ],
            ),
            # 4. Daily Life & Opinion Sharing
            ScenarioDefinition(
                scenario_id="daily.opinion.chat",
                domain="daily_life",
                title="Sharing Opinions & Past Experiences",
                description="Share your impressions about Japanese food and travel experiences.",
                required_skills=["CORE.OPINION", "CORE.EXPERIENCE", "CORE.POSSIBILITY"],
                language_skills=["JP.OPINION.TOOMOU", "JP.EXPERIENCE.TAKOTOGAARU", "JP.POSSIBILITY.KAMOSHIRENAI"],
                vocabulary_domains=["food", "travel", "opinion"],
                difficulty=0.40,
                turns=[
                    ScenarioTurnTemplate(
                        turn_id=1,
                        ai_prompt_text_ja="日本に行ったことがありますか？",
                        ai_prompt_text_en="Have you ever been to Japan?",
                        target_skills=["JP.EXPERIENCE.TAKOTOGAARU"],
                        expected_ir_pattern={"type": "EXPERIENCE", "concept": "JAPAN"},
                        hints="Answer with past experience (e.g. はい、日本に行ったことがあります)",
                    ),
                    ScenarioTurnTemplate(
                        turn_id=2,
                        ai_prompt_text_ja="日本のラーメンはどう思いますか？",
                        ai_prompt_text_en="What do you think about Japanese ramen?",
                        target_skills=["JP.OPINION.TOOMOU"],
                        expected_ir_pattern={"type": "OPINION"},
                        hints="Express your opinion (e.g. 美味しいと思います)",
                    ),
                ],
            ),
            # 5. Travel Directions & Assistance
            ScenarioDefinition(
                scenario_id="travel.direction.ask",
                domain="travel",
                title="Asking for Directions & Transport",
                description="Ask pedestrians or station staff for directions to destination.",
                required_skills=["CORE.LOCATION", "CORE.REQUEST", "CORE.ASK"],
                language_skills=["JP.REQUEST.KUDASAI", "JP.ASK.KA"],
                vocabulary_domains=["location", "transportation"],
                difficulty=0.35,
                turns=[
                    ScenarioTurnTemplate(
                        turn_id=1,
                        ai_prompt_text_ja="すみません、駅はどこですか？",
                        ai_prompt_text_en="Excuse me, where is the train station?",
                        target_skills=["JP.INFORM.DESU", "JP.REQUEST.KUDASAI"],
                        expected_ir_pattern={"concept": "STATION"},
                        hints="Ask or respond with directions (e.g. あそこです)",
                    ),
                ],
            ),
        ]
        for s in scenarios:
            self.register(s)


global_scenarios = ScenarioRegistry()
