"""
Standard Coherent Scenario Episodes for SLA Practice (6 Comprehensive Life Tracks).
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
        # EPISODE 1: 🍽️ 西班牙小吃店點餐記 (Restaurant Tapas) - 4 幕
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="restaurant_tapas",
            icon="🍽️",
            domain="travel",
            title_native={
                "zh-TW": "西班牙小吃店點餐記 (Restaurant Tapas)",
                "zh-CN": "西班牙小吃店点餐记",
                "en": "Tapas Restaurant Adventure"
            },
            description_native={
                "zh-TW": "入座確認預約 ➔ 點選海鮮燉飯 ➔ 索取飲品 ➔ 餐後評價買單",
                "zh-CN": "入座确认预约 ➔ 点选海鲜炖饭 ➔ 索取饮品 ➔ 餐后评价买单",
                "en": "Seating reservation, ordering paella, drinks request, and checkout."
            },
            turns=[
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
                    hints_native={"zh-TW": "回答你有預約（或請給我兩位座位）", "zh-CN": "回答你有预约", "en": "Say you have a reservation"},
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
                        "en": [{"w": "Yes,", "m": "是的"}, {"w": "I have", "m": "我有"}, {"w": "a reservation", "m": "預約"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/4 幕：點選想吃的主餐 (海鮮燉飯)", "zh-CN": "第 2/4 幕：点选想吃的主餐", "en": "Scene 2/4: Ordering Main Dish"},
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
                    hints_native={"zh-TW": "表達渴望（我想吃西班牙海鮮燉飯 / 拉麵）", "zh-CN": "表达渴望", "en": "Express desire to eat"},
                    formula={"es": "[Quiero 我想要] + [comer 吃] + [paella 燉飯]", "ja": "[ラーメンが 拉麵] + [食べたいです 想吃]", "en": "I want to eat paella"},
                    target_skills_universal=["CORE.DESIRE"],
                    target_skills_by_lang={"es": ["ES.DESIRE.QUIERO"], "ja": ["JP.DESIRE.TAI"], "en": ["EN.DESIRE.WANT"]},
                    choices_by_lang={
                        "es": ["Quiero comer paella.", "Quiero comer tapas y paella, por favor."],
                        "ja": ["パエリアを食べたいです。", "ラーメンを食べたいです。"],
                        "en": ["I want to eat paella.", "I want to eat ramen, please."]
                    },
                    words_by_lang={
                        "es": [{"w": "Quiero", "m": "我想要"}, {"w": "comer", "m": "吃"}, {"w": "paella", "m": "燉飯"}, {"w": "ramen", "m": "拉麵"}, {"w": "por favor", "m": "請"}],
                        "ja": [{"w": "パエリアを", "m": "燉飯"}, {"w": "食べたいです", "m": "想吃"}, {"w": "お願いします", "m": "麻煩"}],
                        "en": [{"w": "I want", "m": "想要"}, {"w": "to eat", "m": "吃"}, {"w": "paella", "m": "燉飯"}]
                    }
                ),
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
                    hints_native={"zh-TW": "禮貌請求水或飲料（請給我一杯水 / 啤酒）", "zh-CN": "礼貌请求水", "en": "Politely ask for water"},
                    formula={"es": "[Un vaso de agua 一杯水] + [por favor 請]", "ja": "[お水を 水] + [ください 請給我]", "en": "A glass of water, please"},
                    target_skills_universal=["CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.REQUEST.PORFAVOR"], "ja": ["JP.REQUEST.KUDASAI"], "en": ["EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["Un vaso de agua, por favor.", "Una cerveza fría, por favor."],
                        "ja": ["お水をください。", "冷たいビールをお願いします。"],
                        "en": ["A glass of water, please.", "A cold beer, please."]
                    },
                    words_by_lang={
                        "es": [{"w": "Un vaso de agua,", "m": "一杯水"}, {"w": "Una cerveza,", "m": "一杯啤酒"}, {"w": "por favor", "m": "請/麻煩"}],
                        "ja": [{"w": "お水を", "m": "水"}, {"w": "ビールを", "m": "啤酒"}, {"w": "ください", "m": "請給我"}],
                        "en": [{"w": "A glass of water,", "m": "水"}, {"w": "please", "m": "請"}]
                    }
                ),
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
                    hints_native={"zh-TW": "表達觀點並買單（我覺得非常美味！請給我帳單）", "zh-CN": "表达观点并买单", "en": "Express opinion and ask for check"},
                    formula={"es": "[Creo que 我覺得] + [es muy deliciosa 非常美味] + [La cuenta, por favor 買單]", "ja": "[とても美味しいと 非常美味] + [思います 覺得]", "en": "I think it is delicious. The bill, please."},
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
        # EPISODE 2: 🏨 飯店入住與客房服務 (Hotel Check-in & Requests) - 4 幕
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="hotel_stay",
            icon="🏨",
            domain="travel",
            title_native={
                "zh-TW": "飯店入住與客房服務 (Hotel Check-in & Stay)",
                "zh-CN": "饭店入住与客房服务",
                "en": "Hotel Check-in & Stay"
            },
            description_native={
                "zh-TW": "櫃檯報到 ➔ 詢問 WiFi 密碼與早餐 ➔ 房間冷氣問題反映 ➔ 退房預約計程車",
                "zh-CN": "柜台报到 ➔ 询问 WiFi 密码 ➔ 房间冷气反映 ➔ 退房预约计程车",
                "en": "Check-in, asking for WiFi/breakfast, room AC issue, and taxi booking."
            },
            turns=[
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/4 幕：櫃檯報到與入住手續", "zh-CN": "第 1/4 幕：柜台报到", "en": "Scene 1/4: Check-in"},
                    prompts_target={
                        "es": "¡Buenas tardes! Bienvenido a nuestro hotel. ¿A qué nombre está la reserva?",
                        "ja": "いらっしゃいませ。ご宿泊のお客様ですね。お名前をお願いします。",
                        "en": "Good afternoon! Welcome to our hotel. Under what name is the reservation?"
                    },
                    translations_native={
                        "zh-TW": "午安！歡迎蒞臨本飯店。請問預約登記的是哪位大名？",
                        "zh-CN": "午安！欢迎莅临本饭店。请问预约登记的是哪位大名？",
                        "en": "Good afternoon! Under what name is the reservation?"
                    },
                    hints_native={"zh-TW": "告知姓名與預約（我有預約，名字是陳...）", "zh-CN": "告知姓名", "en": "State reservation name"},
                    formula={"es": "[Tengo una reserva 我有預約] + [a nombre de Chen 以陳為名]", "ja": "[チェンと申します 我叫陳] + [予約があります 有預約]", "en": "I have a reservation under Chen"},
                    target_skills_universal=["CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE"], "ja": ["JP.INFORM.DESU"], "en": ["EN.INFORM"]},
                    choices_by_lang={
                        "es": ["Tengo una reserva a nombre de Chen.", "Hola, aquí está mi pasaporte."],
                        "ja": ["チェンと申します。予約しています。", "こんにちは、パスポートです。"],
                        "en": ["I have a reservation under Chen.", "Hello, here is my passport."]
                    },
                    words_by_lang={
                        "es": [{"w": "Tengo", "m": "我有"}, {"w": "una reserva", "m": "一筆預約"}, {"w": "a nombre de", "m": "以...之名"}, {"w": "mi pasaporte", "m": "我的護照"}],
                        "ja": [{"w": "予約", "m": "預約"}, {"w": "しています", "m": "有做"}, {"w": "パスポートです", "m": "這是護照"}],
                        "en": [{"w": "I have", "m": "我有"}, {"w": "a reservation", "m": "預約"}, {"w": "my passport", "m": "護照"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/4 幕：詢問 WiFi 密碼與早餐時間", "zh-CN": "第 2/4 幕：询问 WiFi", "en": "Scene 2/4: WiFi & Breakfast"},
                    prompts_target={
                        "es": "Aquí tiene la llave de la habitación 302. ¿Tiene alguna pregunta?",
                        "ja": "こちらがお部屋の鍵（302号室）です。何かご質問はございますか？",
                        "en": "Here is your key for room 302. Do you have any questions?"
                    },
                    translations_native={
                        "zh-TW": "這是您 302 號房的鑰匙。請問有任何疑問嗎？",
                        "zh-CN": "这是您 302 号房的钥匙。请问有任何疑问吗？",
                        "en": "Here is your room key. Do you have any questions?"
                    },
                    hints_native={"zh-TW": "詢問密碼或早餐（請問 WiFi 密碼是多少？早餐幾點開始？）", "zh-CN": "询问 WiFi 密码", "en": "Ask for WiFi password"},
                    formula={"es": "[¿Cuál es la contraseña del Wi-Fi? WiFi密碼是什麼？]", "ja": "[Wi-Fiのパスワードは 何ですか？]", "en": "What is the WiFi password?"},
                    target_skills_universal=["CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.REQUEST.PORFAVOR"], "ja": ["JP.REQUEST.KUDASAI"], "en": ["EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["¿Cuál es la contraseña del Wi-Fi, por favor?", "¿A qué hora es el desayuno?"],
                        "ja": ["Wi-Fiのパスワードは何ですか？", "朝食は何時からですか？"],
                        "en": ["What is the Wi-Fi password, please?", "What time is breakfast?"]
                    },
                    words_by_lang={
                        "es": [{"w": "¿Cuál es", "m": "哪一個/什麼"}, {"w": "la contraseña", "m": "密碼"}, {"w": "del Wi-Fi,", "m": "WiFi的"}, {"w": "por favor", "m": "請"}, {"w": "el desayuno", "m": "早餐"}],
                        "ja": [{"w": "Wi-Fiの", "m": "WiFi的"}, {"w": "パスワードは", "m": "密碼"}, {"w": "何ですか？", "m": "是什麼？"}, {"w": "朝食", "m": "早餐"}],
                        "en": [{"w": "What is", "m": "什麼是"}, {"w": "the Wi-Fi password,", "m": "WiFi密碼"}, {"w": "please", "m": "請"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/4 幕：客房冷氣故障反映 (條件與問題)", "zh-CN": "第 3/4 幕：客房冷气反映", "en": "Scene 3/4: AC Issue"},
                    prompts_target={
                        "es": "Recepción, ¿en qué puedo ayudarle?",
                        "ja": "フロントでございます。どうされましたか？",
                        "en": "Front desk, how can I help you?"
                    },
                    translations_native={
                        "zh-TW": "櫃檯您好，請問有什麼能為您服務的？",
                        "zh-CN": "柜台您好，请问有什么能为您服务的？",
                        "en": "Front desk, how can I help you?"
                    },
                    hints_native={"zh-TW": "反映問題（冷氣好像壞了，吹不出冷風）", "zh-CN": "反映冷气问题", "en": "State AC is not working"},
                    formula={"es": "[El aire acondicionado 冷氣] + [no funciona 不運轉]", "ja": "[エアコンが 冷氣] + [動きません 不運作]", "en": "The air conditioner is not working"},
                    target_skills_universal=["CORE.NEGATION"],
                    target_skills_by_lang={"es": ["ES.NEGATION.NO"], "ja": ["JP.NEGATION.NAI"], "en": ["EN.NEGATION.NOT"]},
                    choices_by_lang={
                        "es": ["Disculpe, el aire acondicionado no funciona.", "No hay agua caliente en el baño."],
                        "ja": ["すみません、エアコンが動きません。", "お風呂でお湯が出ません。"],
                        "en": ["Excuse me, the air conditioner is not working.", "There is no hot water in the bathroom."]
                    },
                    words_by_lang={
                        "es": [{"w": "Disculpe,", "m": "不好意思"}, {"w": "el aire acondicionado", "m": "冷氣空調"}, {"w": "no funciona.", "m": "不運轉/故障"}, {"w": "el baño", "m": "浴室"}],
                        "ja": [{"w": "すみません、", "m": "不好意思"}, {"w": "エアコンが", "m": "冷氣"}, {"w": "動きません。", "m": "不動/故障"}],
                        "en": [{"w": "Excuse me,", "m": "不好意思"}, {"w": "the air conditioner", "m": "冷氣"}, {"w": "is not working.", "m": "故障"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=4,
                    step_title={"zh-TW": "第 4/4 幕：退房與預約計程車 (前往機場)", "zh-CN": "第 4/4 幕：退房与预约计程车", "en": "Scene 4/4: Check-out & Taxi"},
                    prompts_target={
                        "es": "¿Va a hacer el check-out ahora? ¿Necesita transporte?",
                        "ja": "チェックアウトですね。お車の手配はいかがですか？",
                        "en": "Checking out now? Do you need transportation?"
                    },
                    translations_native={
                        "zh-TW": "您要辦理退房了嗎？請問需要安排交通工具嗎？",
                        "zh-CN": "您要办理退房了吗？请问需要安排交通工具吗？",
                        "en": "Checking out? Do you need transportation?"
                    },
                    hints_native={"zh-TW": "請求預約計程車（是的，請幫我叫一輛去機場的計程車）", "zh-CN": "请求叫计程车", "en": "Request a taxi to airport"},
                    formula={"es": "[Sí 是的] + [un taxi al aeropuerto 一輛去機場的計程車] + [por favor 請]", "ja": "[空港までのタクシーを 機場計程車] + [お願いします 麻煩]", "en": "A taxi to the airport, please"},
                    target_skills_universal=["CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.REQUEST.PORFAVOR"], "ja": ["JP.REQUEST.KUDASAI"], "en": ["EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["Sí, un taxi al aeropuerto, por favor.", "Muchas gracias por todo, la estancia fue genial."],
                        "ja": ["はい、空港までタクシーをお願いします。", "大変お世話になりました。"],
                        "en": ["Yes, a taxi to the airport, please.", "Thank you very much for everything."]
                    },
                    words_by_lang={
                        "es": [{"w": "Sí,", "m": "是的"}, {"w": "un taxi", "m": "計程車"}, {"w": "al aeropuerto,", "m": "去機場"}, {"w": "por favor", "m": "麻煩/請"}],
                        "ja": [{"w": "はい、", "m": "是的"}, {"w": "空港まで", "m": "到機場"}, {"w": "タクシーを", "m": "計程車"}, {"w": "お願いします", "m": "麻煩"}],
                        "en": [{"w": "Yes,", "m": "是的"}, {"w": "a taxi", "m": "計程車"}, {"w": "to the airport,", "m": "到機場"}, {"w": "please", "m": "請"}]
                    }
                )
            ]
        ))

        # =========================================================================
        # EPISODE 3: ✈️ 機場入境與出遊規劃 (Airport Arrival & Plan) - 4 幕
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="airport_arrival",
            icon="✈️",
            domain="travel",
            title_native={
                "zh-TW": "機場入境與出遊規劃 (Airport & Travel Plan)",
                "zh-CN": "机场入境与出游规划",
                "en": "Airport Arrival & Trip Planning"
            },
            description_native={
                "zh-TW": "海關入境問答 ➔ 詢問前往市區地鐵 ➔ 週末天氣應變 ➔ 景點觀光願望",
                "zh-CN": "海关入境问答 ➔ 询问前往市区地铁 ➔ 周末天气应变 ➔ 景点观光愿望",
                "en": "Immigration Q&A, subway directions, weather contingency, and sightseeing."
            },
            turns=[
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/4 幕：海關入境目的問答", "zh-CN": "第 1/4 幕：海关入境问答", "en": "Scene 1/4: Immigration"},
                    prompts_target={
                        "es": "¿Cuál es el motivo de su visita a España?",
                        "ja": "入国の目的は何ですか？",
                        "en": "What is the purpose of your visit?"
                    },
                    translations_native={
                        "zh-TW": "請問您本次造訪西班牙的目的是什麼？",
                        "zh-CN": "请问您本次造访西班牙的目的是什么？",
                        "en": "What is the purpose of your visit?"
                    },
                    hints_native={"zh-TW": "回答觀光旅遊（我是來觀光旅遊一週）", "zh-CN": "回答观光旅游", "en": "State tourism purpose"},
                    formula={"es": "[Vengo de turismo 我是來觀光的] + [por una semana 待一週]", "ja": "[観光です 觀光] + [一週間滞在します 停留一週]", "en": "Tourism for one week"},
                    target_skills_universal=["CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE"], "ja": ["JP.INFORM.DESU"], "en": ["EN.INFORM"]},
                    choices_by_lang={
                        "es": ["Vengo de turismo por una semana.", "Estoy aquí por negocios."],
                        "ja": ["観光で来ました。一週間滞在します。", "ビジネスです。"],
                        "en": ["I am here for tourism for one week.", "I am here on business."]
                    },
                    words_by_lang={
                        "es": [{"w": "Vengo de turismo", "m": "我是來旅遊觀光的"}, {"w": "por una semana.", "m": "為期一週"}, {"w": "por negocios", "m": "商務"}],
                        "ja": [{"w": "観光で", "m": "為了觀光"}, {"w": "来ました。", "m": "來了"}, {"w": "一週間", "m": "一週"}],
                        "en": [{"w": "For tourism", "m": "為了觀光"}, {"w": "for one week.", "m": "停留一週"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/4 幕：詢問前往市區的地鐵路線", "zh-CN": "第 2/4 幕：询问地鐵", "en": "Scene 2/4: Subway to Center"},
                    prompts_target={
                        "es": "Bienvenido. ¿Sabe cómo llegar al centro de la ciudad?",
                        "ja": "ようこそ。市内中心部への行き方はご存知ですか？",
                        "en": "Welcome. Do you know how to get to the city center?"
                    },
                    translations_native={
                        "zh-TW": "歡迎。請問您知道如何前往市中心嗎？",
                        "zh-CN": "欢迎。请问您知道如何前往市中心吗？",
                        "en": "Welcome. Do you know how to get to the city center?"
                    },
                    hints_native={"zh-TW": "詢問地鐵站在哪（不好意思，請問地鐵站在哪裡？）", "zh-CN": "询问地铁站", "en": "Ask where subway station is"},
                    formula={"es": "[Disculpe 不好意思], [¿dónde está la estación de metro? 地鐵站在哪？]", "ja": "[すみません 不好意思]、[地下鉄の駅はどこですか？ 地鐵站在哪？]", "en": "Where is the subway station?"},
                    target_skills_universal=["CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.REQUEST.PORFAVOR"], "ja": ["JP.REQUEST.KUDASAI"], "en": ["EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["Disculpe, ¿dónde está la estación de metro?", "¿Cómo puedo ir al centro?"],
                        "ja": ["すみません、地下鉄の駅はどこですか？", "市内へはどう行けばいいですか？"],
                        "en": ["Excuse me, where is the subway station?", "How do I get to the center?"]
                    },
                    words_by_lang={
                        "es": [{"w": "Disculpe,", "m": "不好意思"}, {"w": "¿dónde está", "m": "在哪裡"}, {"w": "la estación", "m": "車站"}, {"w": "de metro?", "m": "地鐵"}],
                        "ja": [{"w": "すみません、", "m": "不好意思"}, {"w": "地下鉄の", "m": "地鐵的"}, {"w": "駅はどこですか？", "m": "車站在哪？"}],
                        "en": [{"w": "Excuse me,", "m": "不好意思"}, {"w": "where is", "m": "在哪裡"}, {"w": "the subway station?", "m": "地鐵站"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/4 幕：天氣突發與假設應變 (條件句)", "zh-CN": "第 3/4 幕：天气假设应变", "en": "Scene 3/4: Weather Plan"},
                    prompts_target={
                        "es": "Dicen que el clima no estará bien. Si llueve mañana, ¿qué vas a hacer?",
                        "ja": "明日天気が崩れそうです。もし雨が降ったら、どうしますか？",
                        "en": "They say the weather will be bad. If it rains tomorrow, what will you do?"
                    },
                    translations_native={
                        "zh-TW": "氣象說明天可能會下雨。如果明天下雨，你打算做什麼？",
                        "zh-CN": "气象说明天可能会下雨。如果明天下雨，你打算做什么？",
                        "en": "If it rains tomorrow, what will you do?"
                    },
                    hints_native={"zh-TW": "使用條件句回答（如果下雨我就去博物館 / 待在室內）", "zh-CN": "使用条件句回答", "en": "If it rains, I will go to museum"},
                    formula={"es": "[Si llueve mañana 如果明天下雨], [visitaré el museo 我就去參觀博物館 / no saldré 我就不出門]", "ja": "[もし雨が降ったら 下雨的話]、[博物館に行きます 去博物館]", "en": "If it rains, I will visit museum"},
                    target_skills_universal=["CORE.CONDITION", "CORE.NEGATION"],
                    target_skills_by_lang={"es": ["ES.CONDITION.SI", "ES.NEGATION.NO"], "ja": ["JP.CONDITION.TARA", "JP.NEGATION.NAI"], "en": ["EN.CONDITION.IF", "EN.NEGATION.NOT"]},
                    choices_by_lang={
                        "es": ["Si llueve mañana, visitaré el museo.", "Si llueve, no saldré."],
                        "ja": ["もし雨が降ったら、博物館に行きます。", "雨だったら、行きません。"],
                        "en": ["If it rains tomorrow, I will visit the museum.", "If it rains, I will stay indoors."]
                    },
                    words_by_lang={
                        "es": [{"w": "Si", "m": "如果"}, {"w": "llueve", "m": "下雨"}, {"w": "mañana,", "m": "明天"}, {"w": "no", "m": "不"}, {"w": "visitaré", "m": "參觀"}, {"w": "el museo", "m": "博物館"}],
                        "ja": [{"w": "もし", "m": "如果"}, {"w": "雨が降ったら、", "m": "下雨的話"}, {"w": "博物館に", "m": "去博物館"}, {"w": "行きます", "m": "去"}],
                        "en": [{"w": "If", "m": "如果"}, {"w": "it rains,", "m": "下雨"}, {"w": "I will visit", "m": "我將參觀"}, {"w": "the museum", "m": "博物館"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=4,
                    step_title={"zh-TW": "第 4/4 幕：旅遊景點願望與渴望表達", "zh-CN": "第 4/4 幕：景点愿望", "en": "Scene 4/4: Sightseeing Desires"},
                    prompts_target={
                        "es": "¡Excelente idea! Y además del museo, ¿qué lugares quieres visitar?",
                        "ja": "いいですね！博物館の他に、どこに行きたいですか？",
                        "en": "Great idea! And besides museums, what places do you want to visit?"
                    },
                    translations_native={
                        "zh-TW": "很棒的主意！除了博物館之外，你還想去哪些景點參觀？",
                        "zh-CN": "很棒的主意！除了博物馆之外，你还想去哪些景点参观？",
                        "en": "What other places do you want to visit?"
                    },
                    hints_native={"zh-TW": "表達想去的地方（我想去聖家堂 / 老城區散步）", "zh-CN": "表达想去的地方", "en": "I want to visit the cathedral"},
                    formula={"es": "[Quiero visitar 我想參觀] + [la catedral y la playa 大教堂與海灘]", "ja": "[大聖堂に 大教堂] + [行きたいです 想去]", "en": "I want to visit the old town"},
                    target_skills_universal=["CORE.DESIRE"],
                    target_skills_by_lang={"es": ["ES.DESIRE.QUIERO"], "ja": ["JP.DESIRE.TAI"], "en": ["EN.DESIRE.WANT"]},
                    choices_by_lang={
                        "es": ["Quiero visitar la catedral y el centro histórico.", "Quiero pasear por la playa."],
                        "ja": ["大聖堂と古い街並みに行きたいです。", "海辺を散歩したいです。"],
                        "en": ["I want to visit the cathedral and historic center.", "I want to walk along the beach."]
                    },
                    words_by_lang={
                        "es": [{"w": "Quiero", "m": "我想要"}, {"w": "visitar", "m": "參觀"}, {"w": "la catedral", "m": "大教堂"}, {"w": "el centro histórico", "m": "歷史中心"}, {"w": "la playa", "m": "海灘"}],
                        "ja": [{"w": "大聖堂に", "m": "大教堂"}, {"w": "行きたいです", "m": "想去"}, {"w": "散歩したいです", "m": "想散步"}],
                        "en": [{"w": "I want", "m": "想要"}, {"w": "to visit", "m": "參觀"}, {"w": "the cathedral", "m": "大教堂"}]
                    }
                )
            ]
        ))

        # =========================================================================
        # EPISODE 4: 🛍️ 傳統市集購物與殺價 (Local Market Shopping) - 3 幕
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="market_shopping",
            icon="🛍️",
            domain="shopping",
            title_native={
                "zh-TW": "傳統市集購物與詢價 (Market Shopping)",
                "zh-CN": "传统市集购物与询价",
                "en": "Local Market Shopping"
            },
            description_native={
                "zh-TW": "詢問特產價格 ➔ 試吃與詢問尺寸 ➔ 結帳索取發票",
                "zh-CN": "询问特产价格 ➔ 试吃询问尺寸 ➔ 结账索取发票",
                "en": "Price inquiry, trying samples, and payment receipt."
            },
            turns=[
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/3 幕：詢問火腿與乳酪特產價格", "zh-CN": "第 1/3 幕：询问价格", "en": "Scene 1/3: Price Inquiry"},
                    prompts_target={
                        "es": "¡Hola! Tenemos el mejor jamón ibérico y queso. ¿Qué le gustaría probar?",
                        "ja": "いらっしゃい！新鮮なフルーツと特産品がありますよ。何をお探しですか？",
                        "en": "Hello! We have the best ham and cheese. What would you like to try?"
                    },
                    translations_native={
                        "zh-TW": "你好！我們這裡有最棒的伊比利火腿與乳酪，想看點什麼？",
                        "zh-CN": "你好！我们这里有最棒的火腿，想看点什么？",
                        "en": "What would you like to try?"
                    },
                    hints_native={"zh-TW": "詢問價格（請問這個火腿一公斤多少錢？）", "zh-CN": "询问火腿价格", "en": "Ask for the price"},
                    formula={"es": "[¿Cuánto cuesta 這個多少錢？] + [este jamón, por favor? 這個火腿]", "ja": "[これは 這是] + [いくらですか？ 多少錢？]", "en": "How much is this ham?"},
                    target_skills_universal=["CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.REQUEST.PORFAVOR"], "ja": ["JP.REQUEST.KUDASAI"], "en": ["EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["¿Cuánto cuesta este jamón, por favor?", "¿Puedo probar un poco?"],
                        "ja": ["これはいくらですか？", "試食できますか？"],
                        "en": ["How much is this ham, please?", "Can I try a little?"]
                    },
                    words_by_lang={
                        "es": [{"w": "¿Cuánto cuesta", "m": "多少錢"}, {"w": "este jamón,", "m": "這個火腿"}, {"w": "por favor", "m": "請"}, {"w": "probar", "m": "嘗試/試吃"}],
                        "ja": [{"w": "これは", "m": "這個"}, {"w": "いくらですか？", "m": "多少錢？"}, {"w": "試食", "m": "試吃"}],
                        "en": [{"w": "How much is", "m": "多少錢"}, {"w": "this ham,", "m": "火腿"}, {"w": "please", "m": "請"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/3 幕：表達購買意願與份量", "zh-CN": "第 2/3 幕：表达购买意愿", "en": "Scene 2/3: Quantity Selection"},
                    prompts_target={
                        "es": "Está a 25 euros el kilo. ¿Cuánto le pongo?",
                        "ja": "1キロ25ユーロです。どのくらいお包みしますか？",
                        "en": "It is 25 euros per kilo. How much would you like?"
                    },
                    translations_native={
                        "zh-TW": "一公斤 25 歐元。請問要給您切多少呢？",
                        "zh-CN": "一公斤 25 欧元。请问要给您切多少呢？",
                        "en": "How much would you like?"
                    },
                    hints_native={"zh-TW": "表達需求份量（我想買半公斤 / 200 克，謝謝）", "zh-CN": "表达份量", "en": "I want half a kilo"},
                    formula={"es": "[Quiero 我想要] + [doscientos gramos 200克 / medio kilo 半公斤], [gracias 謝謝]", "ja": "[200グラム 200克] + [ください 請給我]", "en": "I want 200 grams, please"},
                    target_skills_universal=["CORE.DESIRE"],
                    target_skills_by_lang={"es": ["ES.DESIRE.QUIERO"], "ja": ["JP.DESIRE.TAI"], "en": ["EN.DESIRE.WANT"]},
                    choices_by_lang={
                        "es": ["Quiero doscientos gramos, por favor.", "Quiero medio kilo, gracias."],
                        "ja": ["200グラムください。", "半分お願いします。"],
                        "en": ["I want 200 grams, please.", "Half a kilo, thank you."]
                    },
                    words_by_lang={
                        "es": [{"w": "Quiero", "m": "我想要"}, {"w": "doscientos gramos,", "m": "200克"}, {"w": "medio kilo,", "m": "半公斤"}, {"w": "gracias", "m": "謝謝"}],
                        "ja": [{"w": "200グラム", "m": "200克"}, {"w": "ください", "m": "請給我"}, {"w": "お願いします", "m": "麻煩"}],
                        "en": [{"w": "I want", "m": "想要"}, {"w": "200 grams,", "m": "200克"}, {"w": "please", "m": "請"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/3 幕：結帳與索取收據 (現金/信用卡)", "zh-CN": "第 3/3 幕：结账索取收据", "en": "Scene 3/3: Payment & Receipt"},
                    prompts_target={
                        "es": "Aquí tiene. Son 5 euros en total. ¿Paga con tarjeta o en efectivo?",
                        "ja": "合計で5ユーロになります。お支払いはカードですか？現金ですか？",
                        "en": "Here you go. It is 5 euros total. Card or cash?"
                    },
                    translations_native={
                        "zh-TW": "給您。總共是 5 歐元。請問您用刷卡還是現金付費？",
                        "zh-CN": "总共是 5 欧元。请问用刷卡还是现金？",
                        "en": "Card or cash?"
                    },
                    hints_native={"zh-TW": "說明付款方式並索取收據（我用信用卡付款，請給我收據）", "zh-CN": "刷卡付款索取收据", "en": "Pay with card and ask for receipt"},
                    formula={"es": "[Pago con tarjeta 我用信用卡付款] + [el recibo, por favor 請給我收據]", "ja": "[カードで払います 刷卡] + [レシートをください 請給收據]", "en": "With card, and receipt please"},
                    target_skills_universal=["CORE.INFORM", "CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE", "ES.REQUEST.PORFAVOR"], "ja": ["JP.INFORM.DESU", "JP.REQUEST.KUDASAI"], "en": ["EN.INFORM", "EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["Pago con tarjeta. El recibo, por favor.", "En efectivo, aquí tiene 5 euros."],
                        "ja": ["カードでお願いします。レシートをください。", "現金で払います。"],
                        "en": ["I will pay with card. Receipt please.", "In cash, here is 5 euros."]
                    },
                    words_by_lang={
                        "es": [{"w": "Pago con tarjeta.", "m": "我用信用卡付款"}, {"w": "En efectivo,", "m": "現金"}, {"w": "El recibo,", "m": "收據"}, {"w": "por favor", "m": "請"}],
                        "ja": [{"w": "カードで", "m": "用信用卡"}, {"w": "お願いします。", "m": "麻煩了"}, {"w": "レシートを", "m": "收據"}, {"w": "ください", "m": "請給"}],
                        "en": [{"w": "With card.", "m": "刷卡"}, {"w": "The receipt,", "m": "收據"}, {"w": "please", "m": "請"}]
                    }
                )
            ]
        ))

        # =========================================================================
        # EPISODE 5: ☕ 咖啡廳社交與自我介紹 (Cafe Meetup & Social) - 3 幕
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="cafe_social",
            icon="☕",
            domain="social",
            title_native={
                "zh-TW": "咖啡廳社交與自我介紹 (Cafe Meetup & Social)",
                "zh-CN": "咖啡厅社交与自我介绍",
                "en": "Cafe Social Chat & Networking"
            },
            description_native={
                "zh-TW": "打招呼自我介紹 ➔ 詢問職業與興趣 ➔ 交流心得約下次見面",
                "zh-CN": "打招呼自我介绍 ➔ 询问职业兴趣 ➔ 交流心得约下次见面",
                "en": "Introduction, talking about hobbies/jobs, and future plans."
            },
            turns=[
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/3 幕：破冰打招呼與自我介紹", "zh-CN": "第 1/3 幕：自我介绍", "en": "Scene 1/3: Introductions"},
                    prompts_target={
                        "es": "¡Hola! Mucho gusto. ¿De dónde eres?",
                        "ja": "こんにちは！初めまして。ご出身はどちらですか？",
                        "en": "Hello! Nice to meet you. Where are you from?"
                    },
                    translations_native={
                        "zh-TW": "嗨！很高興認識你。請問你是哪裡人呢？",
                        "zh-CN": "嗨！很高兴认识你。请问你是哪里人？",
                        "en": "Where are you from?"
                    },
                    hints_native={"zh-TW": "自我介紹來自台灣（你好！我是台灣人，很高興認識你）", "zh-CN": "自我介绍来自台湾", "en": "I am from Taiwan"},
                    formula={"es": "[Soy de Taiwán 我來自台灣] + [Mucho gusto 很高興認識你]", "ja": "[台湾から来ました 來自台灣] + [よろしくお願いします 請多指教]", "en": "I am from Taiwan, nice to meet you"},
                    target_skills_universal=["CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE"], "ja": ["JP.INFORM.DESU"], "en": ["EN.INFORM"]},
                    choices_by_lang={
                        "es": ["Hola, soy de Taiwán. ¡Mucho gusto!", "Soy Chen, vengo de Taiwán."],
                        "ja": ["こんにちは、台湾から来ました。よろしくお願いします！", "チェンと申します。台湾出身です。"],
                        "en": ["Hello, I am from Taiwan. Nice to meet you!", "I am Chen from Taiwan."]
                    },
                    words_by_lang={
                        "es": [{"w": "Hola,", "m": "你好"}, {"w": "soy de Taiwán.", "m": "我來自台灣"}, {"w": "Mucho gusto!", "m": "很高興認識你"}],
                        "ja": [{"w": "こんにちは、", "m": "你好"}, {"w": "台湾から来ました。", "m": "從台灣來的"}, {"w": "よろしくお願いします", "m": "請多指教"}],
                        "en": [{"w": "Hello,", "m": "你好"}, {"w": "I am from Taiwan.", "m": "我來自台灣"}, {"w": "Nice to meet you!", "m": "很高興認識你"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/3 幕：分享個人興趣與喜好 (渴望與觀點)", "zh-CN": "第 2/3 幕：分享兴趣", "en": "Scene 2/3: Hobbies & Likes"},
                    prompts_target={
                        "es": "¡Qué bien! ¿Qué te gusta hacer en tu tiempo libre?",
                        "ja": "そうなんですね！休みの日は何をするのが好きですか？",
                        "en": "That's cool! What do you like to do in your free time?"
                    },
                    translations_native={
                        "zh-TW": "太棒了！那你平時空閒時間喜歡做些什麼？",
                        "zh-CN": "太棒了！那你平时空闲时间喜欢做什么？",
                        "en": "What do you like to do in your free time?"
                    },
                    hints_native={"zh-TW": "表達喜好（我喜歡學語言、聽音樂和旅行）", "zh-CN": "表达喜好", "en": "I like learning languages and traveling"},
                    formula={"es": "[Me gusta 我喜歡] + [viajar y aprender idiomas 旅行與學語言]", "ja": "[旅行と 旅行與] + [音楽を聴くのが好きです 喜歡聽音樂]", "en": "I like traveling and music"},
                    target_skills_universal=["CORE.DESIRE", "CORE.OPINION"],
                    target_skills_by_lang={"es": ["ES.DESIRE.QUIERO", "ES.OPINION.CREO"], "ja": ["JP.DESIRE.TAI", "JP.OPINION.TOOMOU"], "en": ["EN.DESIRE.WANT", "EN.OPINION.THINK"]},
                    choices_by_lang={
                        "es": ["Me gusta viajar y aprender idiomas.", "Me gusta escuchar música y probar comida nueva."],
                        "ja": ["旅行と言語を学ぶのが好きです。", "音楽を聴くことと美味しいものを食べるのが好きです。"],
                        "en": ["I like traveling and learning languages.", "I like listening to music and trying new food."]
                    },
                    words_by_lang={
                        "es": [{"w": "Me gusta", "m": "我喜歡"}, {"w": "viajar", "m": "旅行"}, {"w": "y", "m": "和"}, {"w": "aprender idiomas.", "m": "學習語言"}, {"w": "escuchar música", "m": "聽音樂"}],
                        "ja": [{"w": "旅行と", "m": "旅行與"}, {"w": "学ぶのが", "m": "學習"}, {"w": "好きです。", "m": "喜歡"}],
                        "en": [{"w": "I like", "m": "我喜歡"}, {"w": "traveling", "m": "旅行"}, {"w": "and learning languages.", "m": "學語言"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/3 幕：約定下次一起出遊 (假設與提議)", "zh-CN": "第 3/3 幕：约定出游", "en": "Scene 3/3: Future Plans"},
                    prompts_target={
                        "es": "¡A mí también! Si tienes tiempo el sábado, ¿vamos a tomar un café?",
                        "ja": "私もです！もし土曜日時間があれば、お茶でもしませんか？",
                        "en": "Me too! If you have time on Saturday, shall we get coffee?"
                    },
                    translations_native={
                        "zh-TW": "我也是！如果週六你有空，我們要不要一起喝杯咖啡？",
                        "zh-CN": "我也是！如果周六你有空，要不要一起喝咖啡？",
                        "en": "If you have time on Saturday, shall we get coffee?"
                    },
                    hints_native={"zh-TW": "接受提議並約定（好啊！如果有空我一定去，週六見！）", "zh-CN": "接受提议", "en": "Great, see you Saturday!"},
                    formula={"es": "[¡Claro! 當然] + [Si no trabajo 如果我沒工作], [vamos 走吧！Nos vemos el sábado 週六見]", "ja": "[ぜひ！ 當然] + [土曜日に会いましょう 週六見]", "en": "Sure! See you on Saturday."},
                    target_skills_universal=["CORE.CONDITION", "CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.CONDITION.SI", "ES.INFORM.PRESENTE"], "ja": ["JP.CONDITION.TARA", "JP.INFORM.DESU"], "en": ["EN.CONDITION.IF", "EN.INFORM"]},
                    choices_by_lang={
                        "es": ["¡Claro que sí! Nos vemos el sábado.", "Me encantaría, si no tengo trabajo voy."],
                        "ja": ["ぜひ！土曜日に会いましょう。", "いいですね、楽しみにしています。"],
                        "en": ["Sure! See you on Saturday.", "I'd love to, if I am free I'll come."]
                    },
                    words_by_lang={
                        "es": [{"w": "¡Claro que sí!", "m": "當然好！"}, {"w": "Nos vemos", "m": "我們相見"}, {"w": "el sábado.", "m": "在週六"}, {"w": "Me encantaría,", "m": "我很想去"}],
                        "ja": [{"w": "ぜひ！", "m": "務必！"}, {"w": "土曜日に", "m": "在週六"}, {"w": "会いましょう。", "m": "見面吧"}],
                        "en": [{"w": "Sure!", "m": "當然"}, {"w": "See you", "m": "再見"}, {"w": "on Saturday.", "m": "週六"}]
                    }
                )
            ]
        ))

        # =========================================================================
        # EPISODE 6: 🏥 藥局諮詢與就醫問答 (Pharmacy & Health Care) - 3 幕
        # =========================================================================
        self.register(ScenarioEpisode(
            episode_id="pharmacy_health",
            icon="🏥",
            domain="health",
            title_native={
                "zh-TW": "藥局諮詢與就醫問答 (Pharmacy & Healthcare)",
                "zh-CN": "药局咨询与就医问答",
                "en": "Pharmacy & Healthcare Consultation"
            },
            description_native={
                "zh-TW": "說明感冒與頭痛症狀 ➔ 詢問服藥方式與注意事項 ➔ 購買藥品與致謝",
                "zh-CN": "说明感冒头痛症状 ➔ 询问服药方式 ➔ 购买药品致谢",
                "en": "Describing headache/cold symptoms, asking dosage, and buying medicine."
            },
            turns=[
                EpisodeTurn(
                    turn_id=1,
                    step_title={"zh-TW": "第 1/3 幕：向藥師說明症狀 (頭痛與發燒)", "zh-CN": "第 1/3 幕：说明症状", "en": "Scene 1/3: Describing Symptoms"},
                    prompts_target={
                        "es": "¡Buenos días! ¿Qué síntomas tiene?",
                        "ja": "こんにちは。今日はどのような症状ですか？",
                        "en": "Good morning! What symptoms do you have?"
                    },
                    translations_native={
                        "zh-TW": "早安！請問您目前有哪些不適症狀？",
                        "zh-CN": "早安！请问您目前有哪些不适症状？",
                        "en": "What symptoms do you have?"
                    },
                    hints_native={"zh-TW": "說明症狀（我頭很痛，而且有點發燒和咳嗽）", "zh-CN": "说明头痛发烧", "en": "I have a headache and fever"},
                    formula={"es": "[Me duele la cabeza 我頭痛] + [y tengo fiebre 而且發燒]", "ja": "[頭が痛くて 頭痛] + [熱があります 發燒]", "en": "I have a headache and fever"},
                    target_skills_universal=["CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE"], "ja": ["JP.INFORM.DESU"], "en": ["EN.INFORM"]},
                    choices_by_lang={
                        "es": ["Me duele la cabeza y tengo un poco de fiebre.", "Tengo dolor de garganta y tos."],
                        "ja": ["頭が痛くて、少し熱があります。", "喉が痛くて咳が出ます。"],
                        "en": ["I have a headache and a mild fever.", "I have a sore throat and cough."]
                    },
                    words_by_lang={
                        "es": [{"w": "Me duele", "m": "我感到痛"}, {"w": "la cabeza", "m": "頭部"}, {"w": "y", "m": "而且"}, {"w": "tengo", "m": "我有"}, {"w": "fiebre.", "m": "發燒"}, {"w": "dolor de garganta", "m": "喉嚨痛"}],
                        "ja": [{"w": "頭が", "m": "頭"}, {"w": "痛くて、", "m": "很痛且"}, {"w": "熱が", "m": "發燒"}, {"w": "あります。", "m": "有"}],
                        "en": [{"w": "I have", "m": "我有"}, {"w": "a headache", "m": "頭痛"}, {"w": "and fever.", "m": "發燒"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=2,
                    step_title={"zh-TW": "第 2/3 幕：詢問服用劑量與注意事項", "zh-CN": "第 2/3 幕：询问服药方式", "en": "Scene 2/3: Dosage & Instructions"},
                    prompts_target={
                        "es": "Aquí tiene este analgésico. ¿Tiene alguna alergia a medicamentos?",
                        "ja": "こちらの解熱鎮痛剤をお出ししますね。お薬のアレルギーはありますか？",
                        "en": "Here is this painkiller. Do you have any drug allergies?"
                    },
                    translations_native={
                        "zh-TW": "為您準備這款止痛退燒藥。請問您對藥物有過敏嗎？",
                        "zh-CN": "为您准备这款止痛退烧药。请问您对药物有过敏吗？",
                        "en": "Do you have any drug allergies?"
                    },
                    hints_native={"zh-TW": "回答無過敏並詢問吃法（沒有過敏。請問一天要吃幾次？）", "zh-CN": "询问一天吃几次", "en": "No allergies. How many times a day?"},
                    formula={"es": "[No tengo alergias 沒有過敏]. [¿Cuántas veces al día debo tomarlo? 一天吃幾次？]", "ja": "[アレルギーはありません 無過敏]。[一日何回飲みますか？ 一天喝幾次？]", "en": "No allergies. How many times a day?"},
                    target_skills_universal=["CORE.NEGATION", "CORE.REQUEST"],
                    target_skills_by_lang={"es": ["ES.NEGATION.NO", "ES.REQUEST.PORFAVOR"], "ja": ["JP.NEGATION.NAI", "JP.REQUEST.KUDASAI"], "en": ["EN.NEGATION.NOT", "EN.REQUEST.PLEASE"]},
                    choices_by_lang={
                        "es": ["No tengo alergias. ¿Cuántas veces al día debo tomarlo?", "No soy alérgico. ¿Es después de comer?"],
                        "ja": ["アレルギーはありません。一日何回飲みますか？", "食後に飲めばいいですか？"],
                        "en": ["No allergies. How many times a day should I take it?", "Is it after meals?"]
                    },
                    words_by_lang={
                        "es": [{"w": "No tengo", "m": "我沒有"}, {"w": "alergias.", "m": "過敏"}, {"w": "¿Cuántas veces", "m": "多少次"}, {"w": "al día", "m": "每天"}, {"w": "tomarlo?", "m": "服用它"}],
                        "ja": [{"w": "アレルギーは", "m": "過敏"}, {"w": "ありません。", "m": "沒有"}, {"w": "一日何回", "m": "一天幾次"}, {"w": "飲みますか？", "m": "服用嗎？"}],
                        "en": [{"w": "No allergies.", "m": "沒有過敏"}, {"w": "How many times", "m": "幾次"}, {"w": "a day?", "m": "一天"}]
                    }
                ),
                EpisodeTurn(
                    turn_id=3,
                    step_title={"zh-TW": "第 3/3 幕：購買藥品與致謝", "zh-CN": "第 3/3 幕：购买致谢", "en": "Scene 3/3: Purchase & Thanks"},
                    prompts_target={
                        "es": "Tome una pastilla cada 8 horas después de comer. ¿Desea algo más?",
                        "ja": "食後に8時間おきに1錠飲んでください。他にご入用のものはございますか？",
                        "en": "Take one pill every 8 hours after meals. Anything else?"
                    },
                    translations_native={
                        "zh-TW": "三餐飯後每 8 小時服用一顆即可。還需要其他東西嗎？",
                        "zh-CN": "三餐饭后每 8 小时服用一颗即可。还需要其他东西吗？",
                        "en": "Take one pill every 8 hours. Anything else?"
                    },
                    hints_native={"zh-TW": "購買並感謝（不用了，只要這個就好。非常感謝您！）", "zh-CN": "只要这个，谢谢", "en": "That is all, thank you very much!"},
                    formula={"es": "[Solo esto, por favor 只要這個就好]. [¡Muchas gracias por su ayuda! 謝謝您的幫忙]", "ja": "[これだけで大丈夫です 只要這個]、[ありがとうございました 謝謝]", "en": "Just this, thank you very much!"},
                    target_skills_universal=["CORE.INFORM"],
                    target_skills_by_lang={"es": ["ES.INFORM.PRESENTE"], "ja": ["JP.INFORM.DESU"], "en": ["EN.INFORM"]},
                    choices_by_lang={
                        "es": ["Solo esto, por favor. ¡Muchas gracias por su ayuda!", "Nada más, muchas gracias."],
                        "ja": ["これだけで大丈夫です。ありがとうございました！", "以上です、ありがとうございます。"],
                        "en": ["Just this, please. Thank you very much for your help!", "Nothing else, thank you."]
                    },
                    words_by_lang={
                        "es": [{"w": "Solo esto,", "m": "只要這個"}, {"w": "por favor.", "m": "麻煩"}, {"w": "¡Muchas gracias", "m": "非常感謝"}, {"w": "por su ayuda!", "m": "您的幫忙"}],
                        "ja": [{"w": "これだけで", "m": "只有這個"}, {"w": "大丈夫です。", "m": "就可以了"}, {"w": "ありがとうございました！", "m": "謝謝您"}],
                        "en": [{"w": "Just this,", "m": "只要這個"}, {"w": "please.", "m": "請"}, {"w": "Thank you", "m": "謝謝"}, {"w": "very much!", "m": "非常"}]
                    }
                )
            ]
        ))


global_scenario_registry = ScenarioRegistry()
global_scenarios = global_scenario_registry
