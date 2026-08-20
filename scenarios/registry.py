"""
Standard Coherent Scenario Episodes for SLA Practice.
"""

from typing import Dict, List, Optional
from scenarios.definitions import ScenarioEpisode, EpisodeTurn


class ScenarioRegistry:
    def __init__(self):
        self._episodes: Dict[str, ScenarioEpisode] = {}
        self._load_standard_episodes()

    def register(self, episode: ScenarioEpisode):
        self._episodes[episode.episode_id] = episode

    def get(self, episode_id: str) -> Optional[ScenarioEpisode]:
        return self._episodes.get(episode_id)

    def list_all(self) -> List[ScenarioEpisode]:
        return list(self._episodes.values())

    def get_by_domain(self, domain: str) -> List[ScenarioEpisode]:
        return [e for e in self._episodes.values() if e.domain == domain]

    def find_best_scenario_for_skills(self, skills: List[str], domain: Optional[str] = None) -> ScenarioEpisode:
        candidates = self.get_by_domain(domain) if domain else self.list_all()
        return candidates[0] if candidates else self.list_all()[0]

    def _load_standard_episodes(self):
        # =========================================================================
        # EPISODE 1: 🍽️ 西班牙小吃店點餐記 (Restaurant Tapas Adventure) - 4 連貫回合
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="restaurant_tapas",
            icon="🍽️",
            domain="travel",
            title_native={
                "zh-TW": "西班牙小吃店點餐記 (Restaurant Adventure)",
                "zh-CN": "西班牙小吃店点餐记",
                "en": "Tapas Restaurant Adventure"
            },
            description_native={
                "zh-TW": "從入座、點選主食、索取飲品到結帳評價的完整連貫情境對話。",
                "zh-CN": "从入座、点选主食、索取饮品到结账评价的完整连贯情境对话。",
                "en": "Complete dining experience: Seating, Ordering food, Drinks, and Checkout."
            },
            turns=[
                # Turn 1: 入座與確認
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/4 幕：入座與確認預約", "zh-CN": "第 1/4 幕：入座与确认预约", "en": "Scene 1/4: Seating & Reservation"},
                    prompts_target={
                        "es": "¡Buenas tardes! Bienvenidos. ¿Tienen una reserva?",
                        "ja": "いらっしゃいませ！ご予約はございますか？",
                        "en": "Good afternoon! Welcome. Do you have a reservation?"
                    },
                    translations_native={
                        "zh-TW": "午安！歡迎光臨。請問您有預約嗎？",
                        "zh-CN": "午安！欢迎光临。请问您有预约吗？",
                        "en": "Good afternoon! Welcome. Do you have a reservation?"
                    },
                    hints_native={
                        "zh-TW": "回答你有預約（或請給我兩位座位）",
                        "zh-CN": "回答你有预约（或请给我两位座位）",
                        "en": "Say you have a reservation or request a table"
                    },
                    formula={"es": "[Sí 有] + [tengo una reserva 我有預約]", "ja": "[はい 有] + [予約しています 有預約]", "en": "Yes, I have a reservation"},
                    target_skills_universal=["CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE"], "ja": ["JP.INFORM.DESU"], "en": ["EN.INFORM"]},
                    choices_by_lang={
                        "es": ["Sí, tengo una reserva.", "Buenas tardes, una mesa para dos, por favor."],
                        "ja": ["はい、予約しています。", "こんにちは、二人席をお願いします。"],
                        "en": ["Yes, I have a reservation.", "A table for two, please."]
                    },
                    words_by_lang={
                        "es": [{"w": "Sí,", "m": "是的"}, {"w": "tengo", "m": "我有"}, {"w": "una", "m": "一個"}, {"w": "reserva", "m": "預約"}, {"w": "por favor", "m": "麻煩/請"}],
                        "ja": [{"w": "はい、", "m": "是的"}, {"w": "予約", "m": "預約"}, {"w": "しています", "m": "有做"}, {"w": "お願いします", "m": "麻煩了"}],
                        "en": [{"w": "Yes,", "m": "是的"}, {"w": "I have", "m": "我有"}, {"w": "a reservation", "m": "預約"}, {"w": "please", "m": "請"}]
                    }
                ),
                # Turn 2: 點選主餐 (想吃海鮮燉飯 / 拉麵)
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/4 幕：點選想吃的主餐", "zh-CN": "第 2/4 幕：点选想吃的主餐", "en": "Scene 2/4: Ordering Main Dish"},
                    prompts_target={
                        "es": "¡Perfecto! Aquí tiene el menú. ¿Qué desea comer hoy?",
                        "ja": "かしこまりました。メニューをどうぞ。何を食べたいですか？",
                        "en": "Great! Here is the menu. What would you like to eat today?"
                    },
                    translations_native={
                        "zh-TW": "太好了！這是菜單。請問您今天想吃點什麼？",
                        "zh-CN": "太好了！这是菜单。请问您今天想吃点什么？",
                        "en": "Great! Here is the menu. What would you like to eat today?"
                    },
                    hints_native={
                        "zh-TW": "表達渴望（我想吃西班牙燉飯 / 拉麵）",
                        "zh-CN": "表达渴望（我想吃西班牙炖饭 / 拉面）",
                        "en": "Express desire to eat something (e.g. I want to eat paella / ramen)"
                    },
                    formula={"es": "[Quiero 我想要] + [comer 吃] + [paella / ramen]", "ja": "[ラーメンが 拉麵] + [食べたいです 想吃]", "en": "I want to eat paella"},
                    target_skills_universal=["CORE.DESIRE"],
                    target_skills_by_lang={"es": ["ES.DESIRE.QUIERO"], "ja": ["JP.DESIRE.TAI"], "en": ["EN.DESIRE.WANT"]},
                    choices_by_lang={
                        "es": ["Quiero comer paella.", "Quiero comer ramen, por favor."],
                        "ja": ["ラーメンを食べたいです。", "パエリアを食べたいです。"],
                        "en": ["I want to eat paella.", "I want to eat ramen, please."]
                    },
                    words_by_lang={
                        "es": [{"w": "Quiero", "m": "我想要"}, {"w": "comer", "m": "吃"}, {"w": "paella", "m": "燉飯"}, {"w": "ramen", "m": "拉麵"}, {"w": "por favor", "m": "請"}],
                        "ja": [{"w": "ラーメンを", "m": "拉麵"}, {"w": "パエリアを", "m": "燉飯"}, {"w": "食べたいです", "m": "想吃"}],
                        "en": [{"w": "I want", "m": "想要"}, {"w": "to eat", "m": "吃"}, {"w": "paella", "m": "燉飯"}, {"w": "please", "m": "請"}]
                    }
                ),
                # Turn 3: 索取水與飲料
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/4 幕：點飲料與索取物品", "zh-CN": "第 3/4 幕：点饮料与索取物品", "en": "Scene 3/4: Drink Request"},
                    prompts_target={
                        "es": "Muy bien. ¿Y qué desea tomar de beber?",
                        "ja": "かしこまりました。お飲み物は何になさいますか？",
                        "en": "Very well. And what would you like to drink?"
                    },
                    translations_native={
                        "zh-TW": "好的。那飲料方面想喝點什麼呢？",
                        "zh-CN": "好的。那饮料方面想喝点什么呢？",
                        "en": "Very well. And what would you like to drink?"
                    },
                    hints_native={
                        "zh-TW": "禮貌請求水或飲料（請給我一杯水 / 啤酒）",
                        "zh-CN": "礼貌请求水或饮料（请给我一杯水 / 啤酒）",
                        "en": "Politely ask for water or beer"
                    },
                    formula={"es": "[Un vaso de agua 一杯水] + [por favor 請]", "ja": "[お水を 水] + [ください 請給我]", "en": "A glass of water, please"},
                    target_skills_universal=["CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.REQUEST.PORFAVOR"], "ja": ["JP.REQUEST.KUDASAI"], "en": ["EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["Un vaso de agua, por favor.", "Una cerveza, por favor."],
                        "ja": ["お水をください。", "ビールをお願いします。"],
                        "en": ["A glass of water, please.", "A beer, please."]
                    },
                    words_by_lang={
                        "es": [{"w": "Un vaso de agua,", "m": "一杯水"}, {"w": "Una cerveza,", "m": "一杯啤酒"}, {"w": "por favor", "m": "請/麻煩"}],
                        "ja": [{"w": "お水を", "m": "水"}, {"w": "ビールを", "m": "啤酒"}, {"w": "ください", "m": "請給我"}, {"w": "お願いします", "m": "麻煩"}],
                        "en": [{"w": "A glass of water,", "m": "水"}, {"w": "please", "m": "請"}]
                    }
                ),
                # Turn 4: 結帳與評價
                EpisodeTurn(
                    turn_id=4,
                    step_title={"zh-TW": "第 4/4 幕：餐後評價與索取帳單", "zh-CN": "第 4/4 幕：餐后评价与索取账单", "en": "Scene 4/4: Feedback & Check"},
                    prompts_target={
                        "es": "¿Qué le pareció la comida?",
                        "ja": "お食事はいかがでしたか？",
                        "en": "How was the food?"
                    },
                    translations_native={
                        "zh-TW": "今天的餐點合您的胃口嗎？",
                        "zh-CN": "今天的餐点合您的胃口吗？",
                        "en": "How was the food?"
                    },
                    hints_native={
                        "zh-TW": "表達主觀觀點（我覺得非常美味！請給我帳單）",
                        "zh-CN": "表达主观观点（我觉得非常美味！请给我账单）",
                        "en": "Express opinion (I think it is delicious! The bill, please)"
                    },
                    formula={"es": "[Creo que 我覺得] + [es muy deliciosa 非常美味]", "ja": "[とても美味しいと 非常美味] + [思います 我覺得]", "en": "I think it is very delicious"},
                    target_skills_universal=["CORE.OPINION"],
                    target_skills_by_lang={"es": ["ES.OPINION.CREO"], "ja": ["JP.OPINION.TOOMOU"], "en": ["EN.OPINION.THINK"]},
                    choices_by_lang={
                        "es": ["Creo que es muy deliciosa. La cuenta, por favor.", "¡Estuvo excelente! Muchas gracias."],
                        "ja": ["とても美味しいと思います。お会計をお願いします。", "すごく美味しかったです。"],
                        "en": ["I think it is very delicious. The bill, please.", "It was great! Thank you."]
                    },
                    words_by_lang={
                        "es": [{"w": "Creo que", "m": "我覺得"}, {"w": "es muy deliciosa.", "m": "非常美味"}, {"w": "La cuenta,", "m": "帳單"}, {"w": "por favor", "m": "請"}],
                        "ja": [{"w": "とても", "m": "非常"}, {"w": "美味しいと", "m": "美味"}, {"w": "思います", "m": "覺得"}, {"w": "お会計を", "m": "結帳"}],
                        "en": [{"w": "I think", "m": "我覺得"}, {"w": "it is delicious.", "m": "美味"}, {"w": "The bill, please", "m": "買單"}]
                    }
                )
            ]
        ))

        # =========================================================================
        # EPISODE 2: 🌦️ 週末出遊與天氣突發 (Weekend Trip & Weather) - 3 連貫回合
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="weekend_trip",
            icon="🌦️",
            domain="daily",
            title_native={
                "zh-TW": "週末出遊與天氣應變 (Weekend Trip & Plan)",
                "zh-CN": "周末出游与天气应变",
                "en": "Weekend Trip & Weather Plan"
            },
            description_native={
                "zh-TW": "與朋友討論出遊計劃、針對下雨做假設條件應對，並分享經驗。",
                "zh-CN": "与朋友讨论出游计划、针对下雨做假设条件应对，并分享经验。",
                "en": "Discussing trip plans, weather contingencies, and past experiences."
            },
            turns=[
                # Turn 1: 目的地提議
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/3 幕：討論週末出遊想做的事", "zh-CN": "第 1/3 幕：讨论周末出游想做的事", "en": "Scene 1/3: Trip Activity"},
                    prompts_target={
                        "es": "Este fin de semana vamos a Madrid. ¿Qué quieres hacer?",
                        "ja": "今週末は東京に行きます。何をしたいですか？",
                        "en": "This weekend we are going to Madrid. What do you want to do?"
                    },
                    translations_native={
                        "zh-TW": "這個週末我們要去馬德里。你想做些什麼呢？",
                        "zh-CN": "这个周末我们要去马德里。你想做些什么呢？",
                        "en": "This weekend we are going to Madrid. What do you want to do?"
                    },
                    hints_native={
                        "zh-TW": "表達想做的事情（例如：我想吃美食 / 參觀博物館）",
                        "zh-CN": "表达想做的事情（例如：我想吃美食 / 参观博物馆）",
                        "en": "State what you want to do (e.g. I want to visit museums / eat tapas)"
                    },
                    formula={"es": "[Quiero 我想要] + [visitar 參觀] / [comer 吃美食]", "ja": "[美味しいものを 美食] + [食べたいです 想吃]", "en": "I want to visit museums"},
                    target_skills_universal=["CORE.DESIRE"],
                    target_skills_by_lang={"es": ["ES.DESIRE.QUIERO"], "ja": ["JP.DESIRE.TAI"], "en": ["EN.DESIRE.WANT"]},
                    choices_by_lang={
                        "es": ["Quiero comer tapas y pasear.", "Quiero visitar la ciudad."],
                        "ja": ["美味しいものを食べたいです。", "街を散歩したいです。"],
                        "en": ["I want to eat tapas and walk around.", "I want to visit the city."]
                    },
                    words_by_lang={
                        "es": [{"w": "Quiero", "m": "我想要"}, {"w": "comer tapas", "m": "吃小吃"}, {"w": "visitar", "m": "參觀"}, {"w": "pasear", "m": "散步"}],
                        "ja": [{"w": "美味しいものを", "m": "美食"}, {"w": "食べたいです", "m": "想吃"}, {"w": "散歩したいです", "m": "想散步"}],
                        "en": [{"w": "I want", "m": "想要"}, {"w": "to eat", "m": "吃"}, {"w": "to walk", "m": "散步"}]
                    }
                ),
                # Turn 2: 天氣假設條件
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/3 幕：天候假設與應變 (條件句)", "zh-CN": "第 2/3 幕：天候假设与应变", "en": "Scene 2/3: Weather Contingency"},
                    prompts_target={
                        "es": "Dicen que el clima no estará bien. Si llueve mañana, ¿qué vas a hacer?",
                        "ja": "天気が悪くなりそうです。明日雨が降ったら、どうしますか？",
                        "en": "They say the weather might be bad. If it rains tomorrow, what will you do?"
                    },
                    translations_native={
                        "zh-TW": "氣象說天氣可能會變差。如果明天下雨，你打算怎麼辦？",
                        "zh-CN": "气象说天气可能会变差。如果明天下雨，你打算怎么办？",
                        "en": "The weather might be bad. If it rains tomorrow, what will you do?"
                    },
                    hints_native={
                        "zh-TW": "使用條件句表達應對（如果下雨我就不出門 / 待在家裡）",
                        "zh-CN": "使用条件句表达应对（如果下雨我就不出门 / 待在家里）",
                        "en": "Express conditional response (If it rains, I will stay home / not go out)"
                    },
                    formula={"es": "[Si 如果] + [llueve 下雨], [no saldré 不出門 / me quedo en casa 待在家]", "ja": "[明日] + [雨が降ったら 下雨的話]、[行きません 不去]", "en": "If it rains, I will stay home"},
                    target_skills_universal=["CORE.CONDITION", "CORE.NEGATION"],
                    target_skills_by_lang={"es": ["ES.CONDITION.SI", "ES.NEGATION.NO"], "ja": ["JP.CONDITION.TARA", "JP.NEGATION.NAI"], "en": ["EN.CONDITION.IF", "EN.NEGATION.NOT"]},
                    choices_by_lang={
                        "es": ["Si llueve mañana, no saldré.", "Si llueve, me quedo en el hotel."],
                        "ja": ["明日雨が降ったら、行きません。", "雨だったら、ホテルで休みます。"],
                        "en": ["If it rains tomorrow, I will not go out.", "If it rains, I will stay at the hotel."]
                    },
                    words_by_lang={
                        "es": [{"w": "Si", "m": "如果"}, {"w": "llueve", "m": "下雨"}, {"w": "mañana,", "m": "明天"}, {"w": "no", "m": "不"}, {"w": "saldré", "m": "出門"}, {"w": "me quedo", "m": "待在"}, {"w": "en el hotel", "m": "飯店"}],
                        "ja": [{"w": "明日", "m": "明天"}, {"w": "雨が降ったら", "m": "如果下雨"}, {"w": "行きません", "m": "不去"}, {"w": "ホテルで", "m": "在飯店"}, {"w": "休みます", "m": "休息"}],
                        "en": [{"w": "If", "m": "如果"}, {"w": "it rains", "m": "下雨"}, {"w": "I will not", "m": "我不"}, {"w": "go out", "m": "出門"}]
                    }
                ),
                # Turn 3: 過去經驗分享
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/3 幕：旅遊經驗分享 (過去經驗句)", "zh-CN": "第 3/3 幕：旅游经验分享", "en": "Scene 3/3: Experience Sharing"},
                    prompts_target={
                        "es": "¿Has estado en España antes?",
                        "ja": "日本に行ったことがありますか？",
                        "en": "Have you ever been to Spain before?"
                    },
                    translations_native={
                        "zh-TW": "你以前曾經去過西班牙嗎？",
                        "zh-CN": "你以前曾经去过西班牙吗？",
                        "en": "Have you ever been to Spain before?"
                    },
                    hints_native={
                        "zh-TW": "分享過去經驗（我有去過一次 / 從沒去過）",
                        "zh-CN": "分享过去经验（我有去过一次 / 从没去过）",
                        "en": "Share past experience (Yes, I have been / No, never)"
                    },
                    formula={"es": "[Sí, 有] + [he estado 我曾去過] [en España 在西班牙]", "ja": "[はい 有] + [行ったことがあります 曾去過]", "en": "Yes, I have been to Spain"},
                    target_skills_universal=["CORE.EXPERIENCE"],
                    target_skills_by_lang={"es": ["ES.EXPERIENCE.HABER"], "ja": ["JP.EXPERIENCE.TAKOTOGAARU"], "en": ["EN.EXPERIENCE.HAVE_BEEN"]},
                    choices_by_lang={
                        "es": ["Sí, he estado en España.", "No, nunca he estado allí."],
                        "ja": ["はい、日本に行ったことがあります。", "いいえ、行ったことがありません。"],
                        "en": ["Yes, I have been to Spain.", "No, I have never been there."]
                    },
                    words_by_lang={
                        "es": [{"w": "Sí,", "m": "是的"}, {"w": "he estado", "m": "我曾去過"}, {"w": "en España", "m": "在西班牙"}, {"w": "No,", "m": "沒有"}, {"w": "nunca", "m": "從未"}],
                        "ja": [{"w": "はい、", "m": "是的"}, {"w": "日本に", "m": "去日本"}, {"w": "行ったことがあります", "m": "曾經去過"}, {"w": "いいえ、", "m": "沒有"}],
                        "en": [{"w": "Yes,", "m": "是的"}, {"w": "I have been", "m": "我曾去過"}, {"w": "to Spain", "m": "去西班牙"}]
                    }
                )
            ]
        ))


global_scenario_registry = ScenarioRegistry()
global_scenarios = global_scenario_registry
