"""
Registry of standard conversation scenarios with clean native/target separation.
"""

from typing import Dict, List, Optional
from scenarios.definitions import Scenario, MultilingualPrompt
from core.ir_schema import CommunicationIR, IntentNode, ContentNode
from core.primitives import IntentPrimitive


class ScenarioRegistry:
    def __init__(self):
        self._scenarios: Dict[str, Scenario] = {}
        self._load_standard_scenarios()

    def register(self, scenario: Scenario):
        self._scenarios[scenario.scenario_id] = scenario

    def get(self, scenario_id: str) -> Optional[Scenario]:
        return self._scenarios.get(scenario_id)

    def list_all(self) -> List[Scenario]:
        return list(self._scenarios.values())

    def _load_standard_scenarios(self):
        # 1. Weather Plan (Condition / Negation)
        self.register(Scenario(
            scenario_id="daily.weather.plan",
            domain="daily",
            title_native={
                "zh-TW": "天氣與出行計劃",
                "zh-CN": "天气与出行计划",
                "en": "Weather & Travel Plan"
            },
            description_native={
                "zh-TW": "練習當遇到天候變化時的假設條件句與否定表達。",
                "zh-CN": "练习当遇到天气变化时的假设条件句与否定表达。",
                "en": "Practice hypothetical condition and negation for weather plans."
            },
            difficulty_level=1,
            prompt_data=MultilingualPrompt(
                prompts_target={
                    "ja": "明日雨が降ったら、どうしますか？",
                    "es": "Si llueve mañana, ¿qué vas a hacer?",
                    "en": "If it rains tomorrow, what will you do?"
                },
                translations_native={
                    "zh-TW": "如果明天下雨，你打算做什麼？",
                    "zh-CN": "如果明天下雨，你打算做什么？",
                    "en": "If it rains tomorrow, what will you do?"
                },
                hints_native={
                    "zh-TW": "表達條件與行動（例如：如果下雨我就不出門 / 待在家裡）",
                    "zh-CN": "表达条件与行动（例如：如果下雨我就不出门 / 待在家里）",
                    "en": "Express condition and consequence (e.g., If it rains, I will stay home / not go out)"
                },
                target_skills_universal=["CORE.CONDITION", "CORE.NEGATION"],
                target_skills_by_lang={
                    "ja": ["JP.CONDITION.TARA", "JP.NEGATION.NAI"],
                    "es": ["ES.CONDITION.SI", "ES.NEGATION.NO"],
                    "en": ["EN.CONDITION.IF", "EN.NEGATION.NOT"]
                }
            ),
            expected_ir=CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="CONDITION",
                    condition={"type": "EVENT", "predicate": "RAIN", "time": {"type": "TIME", "value": "tomorrow"}},
                    consequence={"type": "NEGATION", "scope": {"type": "EVENT", "predicate": "GO"}}
                )
            )
        ))

        # 2. Restaurant Order (Desire / Request)
        self.register(Scenario(
            scenario_id="travel.restaurant.order",
            domain="travel",
            title_native={
                "zh-TW": "餐廳點餐與需求",
                "zh-CN": "餐厅点餐与需求",
                "en": "Restaurant Ordering"
            },
            description_native={
                "zh-TW": "練習在餐廳向店員點餐或索取水與菜單。",
                "zh-CN": "练习在餐厅向店员点餐或索取水与菜单。",
                "en": "Practice ordering food or asking for water/menu."
            },
            difficulty_level=1,
            prompt_data=MultilingualPrompt(
                prompts_target={
                    "ja": "いらっしゃいませ！ご注文はお決まりですか？",
                    "es": "¡Bienvenido! ¿Qué desea pedir?",
                    "en": "Welcome! What would you like to order?"
                },
                translations_native={
                    "zh-TW": "歡迎光臨！請問您決定好點什麼了嗎？",
                    "zh-CN": "欢迎光临！请问您决定好点什么了吗？",
                    "en": "Welcome! What would you like to order?"
                },
                hints_native={
                    "zh-TW": "表達點餐渴望或禮貌請求（例如：我想吃拉麵 / 請給我一杯水）",
                    "zh-CN": "表达点餐渴望或礼貌请求（例如：我想吃拉面 / 请给我一杯水）",
                    "en": "Express desire or request (e.g., I want to eat ramen / Water, please)"
                },
                target_skills_universal=["CORE.DESIRE", "CORE.REQUEST"],
                target_skills_by_lang={
                    "ja": ["JP.DESIRE.TAI", "JP.REQUEST.KUDASAI"],
                    "es": ["ES.DESIRE.QUIERO", "ES.REQUEST.PORFAVOR"],
                    "en": ["EN.DESIRE.WANT", "EN.REQUEST.PLEASE"]
                }
            ),
            expected_ir=CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.REQUEST),
                content=ContentNode(type="ACTION", predicate="PROVIDE", arguments={"patient": {"type": "ENTITY", "concept": "RAMEN"}})
            )
        ))

        # 3. Travel Experience & Opinion
        self.register(Scenario(
            scenario_id="daily.opinion.chat",
            domain="daily",
            title_native={
                "zh-TW": "旅遊經驗與心得",
                "zh-CN": "旅游经验与心得",
                "en": "Travel Experience & Opinion"
            },
            description_native={
                "zh-TW": "練習分享過去旅遊經歷與個人主觀評價。",
                "zh-CN": "练习分享过去旅游经历与个人主观评价。",
                "en": "Practice sharing past experiences and personal thoughts."
            },
            difficulty_level=2,
            prompt_data=MultilingualPrompt(
                prompts_target={
                    "ja": "日本に行ったことがありますか？ラーメンはどう思いますか？",
                    "es": "¿Ha estado en Japón alguna vez? ¿Qué piensa del ramen?",
                    "en": "Have you ever been to Japan? What do you think of ramen?"
                },
                translations_native={
                    "zh-TW": "你曾去過日本嗎？你覺得拉麵怎麼樣？",
                    "zh-CN": "你曾去过日本吗？你觉得拉面怎么样？",
                    "en": "Have you ever been to Japan? What do you think of ramen?"
                },
                hints_native={
                    "zh-TW": "表達經驗與看法（例如：我有去過日本 / 我覺得非常好吃）",
                    "zh-CN": "表达经验与看法（例如：我有去过日本 / 我觉得非常美味）",
                    "en": "Express experience and opinion (e.g., I have been to Japan / I think it is delicious)"
                },
                target_skills_universal=["CORE.EXPERIENCE", "CORE.OPINION"],
                target_skills_by_lang={
                    "ja": ["JP.EXPERIENCE.TAKOTOGAARU", "JP.OPINION.TOOMOU"],
                    "es": ["ES.EXPERIENCE.HABER", "ES.OPINION.CREO"],
                    "en": ["EN.EXPERIENCE.HAVE_BEEN", "EN.OPINION.THINK"]
                }
            ),
            expected_ir=CommunicationIR(
                intent=IntentNode(type=IntentPrimitive.INFORM),
                content=ContentNode(
                    type="EVENT",
                    predicate="GO",
                    arguments={"destination": {"type": "ENTITY", "concept": "JAPAN"}},
                    extra={"aspect": "EXPERIENCE"}
                )
            )
        ))


global_scenario_registry = ScenarioRegistry()
