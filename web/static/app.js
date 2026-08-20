// ACAS Web Client Logic
let turnStartTime = Date.now();
let currentLearnerId = "web_user";
let targetLanguage = "es";
let nativeLanguage = "zh-TW";
let isBeginnerMode = true;
let currentPromptData = null;

const API_BASE = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return API_BASE + cleanPath;
}

// Multilingual UI dictionary for native language switching
const I18N = {
  "zh-TW": {
    missionTitle: "🚩 當前學習任務 (Current Mission)",
    missionGoalCond: "任務：回答當明天下雨時，你的應對行動（練習條件句表達）。",
    missionGoalDesire: "任務：在餐廳向服務生表達想吃的餐點或需求（練習渴望/請求表達）。",
    missionGoalExp: "任務：分享自己是否有前往特定國家旅遊的經驗（練習過去經驗表達）。",
    missionGoalOp: "任務：表達你對特定食物或地方的主觀看法（練習觀點表達）。",
    missionGoalDir: "任務：向路人詢問前往車站或目的地的方向（練習問路表達）。",
    missionGoalGen: "任務：根據 AI 的提問，給出符合意圖的自然回答。",
    placeholder: "可直接輸入目標語言、母語意向 (如: 下雨就不出門)，或點選上方積木...",
    speechTip: "點擊發音 🔊"
  },
  "zh-CN": {
    missionTitle: "🚩 当前学习任务 (Current Mission)",
    missionGoalCond: "任务：回答当明天下雨时，你的应对行动（练习条件句表达）。",
    missionGoalDesire: "任务：在餐厅向服务员表达想吃的餐点或需求（练习渴望/请求表达）。",
    missionGoalExp: "任务：分享自己是否有前往特定国家旅游的经验（练习过去经验表达）。",
    missionGoalOp: "任务：表达你对特定食物或地方的主观态度（练习观点表达）。",
    missionGoalDir: "任务：向路人询问前往车站或目的地的方向（练习问路表达）。",
    missionGoalGen: "任务：根据 AI 的提问，给出符合意图的自然回答。",
    placeholder: "可直接输入目标语言、母语意向 (如: 下雨就不出门)，或点选上方积木...",
    speechTip: "点击发音 🔊"
  },
  "en": {
    missionTitle: "🚩 Current Mission Target",
    missionGoalCond: "Mission: State what you will do if it rains tomorrow (Practice Conditionals).",
    missionGoalDesire: "Mission: Order food or express desire at a restaurant (Practice Desires/Requests).",
    missionGoalExp: "Mission: Share whether you have visited a foreign country (Practice Experiences).",
    missionGoalOp: "Mission: Give your opinion about a dish or place (Practice Opinions).",
    missionGoalDir: "Mission: Ask for directions to the station (Practice Location Inquiries).",
    missionGoalGen: "Mission: Answer naturally according to the prompt.",
    placeholder: "Type in target language, native intent (e.g. will not go if rain), or click blocks...",
    speechTip: "Listen Audio 🔊"
  }
};

function changeNativeLanguage(lang) {
  nativeLanguage = lang;
  updateMissionDisplay();
  if (currentPromptData) {
    renderScaffolding(currentPromptData.prompt_target_lang);
  }
}

function changeTargetLanguage(lang) {
  targetLanguage = lang;
  const labelMap = { es: "🇪🇸 西班牙語", ja: "🇯🇵 日語", en: "🇬🇧 英語" };
  document.getElementById('current-lang-display').innerText = labelMap[lang] || lang;
  
  document.getElementById('chat-messages').innerHTML = '';
  loadNextTurn();
  loadProgress();
}

function openTutorialModal() {
  document.getElementById('tutorial-modal').classList.add('active');
}

function closeTutorialModal() {
  document.getElementById('tutorial-modal').classList.remove('active');
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  event.target.classList.add('active');

  if (tabId === 'skills-tab') loadSkills();
  if (tabId === 'analytics-tab') loadProgress();
}

function toggleBeginnerMode() {
  const toggle = document.getElementById('beginner-mode-toggle');
  isBeginnerMode = toggle.checked;
  document.getElementById('scaffolding-panel').style.display = isBeginnerMode ? 'block' : 'none';
}

function speakText(text, lang) {
  if ('speechSynthesis' in window) {
    const langCode = lang || (targetLanguage === 'es' ? 'es-ES' : (targetLanguage === 'en' ? 'en-US' : 'ja-JP'));
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.88;
    window.speechSynthesis.speak(utterance);
  }
}

// Scaffolding database with full native annotations
const MISSIONS_DB = {
  "weather": {
    formula_es: "[Si 如果] + [llueve 下雨], [no saldré / no voy 我不出門]",
    formula_ja: "[明日] + [雨が降ったら 下雨的話]、[行きません 不去]",
    formula_en: "If [it rains], [I will not go]",
    skill: "CORE.CONDITION",
    goalKey: "missionGoalCond",
    es: {
      options: [
        { text: "Si llueve mañana, no saldré.", zh: "如果明天下雨，我就不出門。" },
        { text: "Si llueve, me quedo en casa.", zh: "如果下雨，我就待在家。" },
        { text: "No voy si llueve mañana.", zh: "如果明天下雨我不會去。" }
      ],
      words: [
        { w: "Si", m: "如果" }, { w: "llueve", m: "下雨" }, { w: "mañana,", m: "明天" },
        { w: "no", m: "不" }, { w: "saldré", m: "出門" }, { w: "voy", m: "去" },
        { w: "me quedo", m: "待在" }, { w: "en casa", m: "家裡" }, { w: "a Tokio", m: "去東京" }
      ]
    },
    ja: {
      options: [
        { text: "明日雨が降ったら、行きません。", zh: "如果明天下雨，我就不去。" },
        { text: "明日雨が降ったら、家で休みます。", zh: "如果明天下雨，就在家休息。" },
        { text: "雨だったら、出かけない。", zh: "如果下雨就不出門 (常體)。" }
      ],
      words: [
        { w: "明日", m: "明天" }, { w: "雨が降ったら", m: "如果下雨" }, { w: "東京に", m: "去東京" },
        { w: "行きません", m: "不去" }, { w: "出かけない", m: "不出門" }, { w: "家で", m: "在家" },
        { w: "休みます", m: "休息" }, { w: "映画を", m: "看電影" }
      ]
    }
  },
  "restaurant": {
    formula_es: "[Quiero 想吃] + [ramen 拉麵] / [Un vaso de agua 一杯水], [por favor 請]",
    formula_ja: "[ラーメンを 拉麵] + [食べたいです 想吃] / [お水を 水を] + [ください 請給我]",
    formula_en: "I want [ramen] / [Water], please",
    skill: "CORE.REQUEST / DESIRE",
    goalKey: "missionGoalDesire",
    es: {
      options: [
        { text: "Quiero comer ramen.", zh: "我想吃拉麵。" },
        { text: "Un vaso de agua, por favor.", zh: "請給我一杯水。" },
        { text: "El menú, por favor.", zh: "請給我菜單。" }
      ],
      words: [
        { w: "Quiero", m: "我想要" }, { w: "comer", m: "吃" }, { w: "ramen", m: "拉麵" },
        { w: "Un vaso de agua,", m: "一杯水" }, { w: "El menú,", m: "菜單" }, { w: "por favor", m: "請/麻煩" }
      ]
    },
    ja: {
      options: [
        { text: "ラーメンをください。", zh: "請給我一碗拉麵。" },
        { text: "ラーメンが食べたいです。", zh: "我想吃拉麵。" },
        { text: "お水をください。", zh: "請給我一杯水。" }
      ],
      words: [
        { w: "ラーメンを", m: "拉麵" }, { w: "お水を", m: "水" }, { w: "メニューを", m: "菜單" },
        { w: "ください", m: "請給我" }, { w: "食べたいです", m: "想吃" }, { w: "お願いします", m: "麻煩了" }
      ]
    }
  },
  "hotel": {
    formula_es: "[Tengo 有] + [una reserva 一筆預約] [a nombre de 名義]",
    formula_ja: "[田中です 我是田中]",
    formula_en: "I have a reservation under Tanaka",
    skill: "CORE.INFORM",
    goalKey: "missionGoalGen",
    es: {
      options: [
        { text: "Tengo una reserva a nombre de Tanaka.", zh: "我有一筆以 Tanaka 名義的預約。" },
        { text: "Sí, tengo una reserva.", zh: "是的，我有預約。" }
      ],
      words: [
        { w: "Tengo", m: "我有" }, { w: "una reserva", m: "預約" }, { w: "a nombre de", m: "名字是" },
        { w: "Tanaka", m: "田中" }, { w: "Sí,", m: "是的" }
      ]
    },
    ja: {
      options: [
        { text: "田中です。予約しています。", zh: "我是田中，有預約。" },
        { text: "予約の確認をお願いします。", zh: "麻煩確認預約。" }
      ],
      words: [
        { w: "田中です", m: "我是田中" }, { w: "予約しています", m: "有預約" }, { w: "お願いします", m: "麻煩了" }
      ]
    }
  },
  "opinion": {
    formula_es: "[Creo que 我覺得] + [es muy delicioso 非常美味]",
    formula_ja: "[日本に行ったことがある 去過日本] / [美味しいと思います 覺得美味]",
    formula_en: "I think it is delicious",
    skill: "CORE.OPINION / EXPERIENCE",
    goalKey: "missionGoalExp",
    es: {
      options: [
        { text: "Sí, he estado en Japón.", zh: "有，我曾經去過日本。" },
        { text: "Creo que es muy delicioso.", zh: "我覺得非常美味。" },
        { text: "No, nunca he estado allí.", zh: "沒有，我從未去過那裡。" }
      ],
      words: [
        { w: "Sí,", m: "有/是的" }, { w: "he estado", m: "我曾去過" }, { w: "en Japón", m: "在日本" },
        { w: "Creo que", m: "我覺得" }, { w: "es muy delicioso", m: "非常美味" }, { w: "nunca", m: "從未" }
      ]
    },
    ja: {
      options: [
        { text: "はい、日本に行ったことがあります。", zh: "有，我曾經去過日本。" },
        { text: "とても美味しいと思います。", zh: "我覺得非常美味。" },
        { text: "いいえ、行ったことがありません。", zh: "沒有，我還沒去過。" }
      ],
      words: [
        { w: "はい、", m: "是的/有" }, { w: "日本に", m: "去日本" }, { w: "行ったことがあります", m: "曾經去過" },
        { w: "とても美味しいと", m: "非常美味" }, { w: "思います", m: "我覺得" }
      ]
    }
  }
};

function updateMissionDisplay() {
  const i18n = I18N[nativeLanguage] || I18N["zh-TW"];
  document.getElementById('user-input').placeholder = i18n.placeholder;

  let missionKey = "weather";
  if (currentPromptData) {
    const sc = currentPromptData.scenario_id || "";
    if (sc.includes("restaurant")) missionKey = "restaurant";
    else if (sc.includes("hotel")) missionKey = "hotel";
    else if (sc.includes("opinion")) missionKey = "opinion";
  }

  const mData = MISSIONS_DB[missionKey] || MISSIONS_DB["weather"];
  document.getElementById('target-skill-badge').innerText = mData.skill;
  document.getElementById('mission-goal-text').innerText = i18n[mData.goalKey] || i18n.missionGoalGen;

  const formula = targetLanguage === 'es' ? mData.formula_es : (targetLanguage === 'ja' ? mData.formula_ja : mData.formula_en);
  document.getElementById('mission-formula').innerText = formula;
}

function renderScaffolding(promptText) {
  updateMissionDisplay();

  const optContainer = document.getElementById('quick-options-container');
  const wordContainer = document.getElementById('word-chips-container');
  optContainer.innerHTML = '';
  wordContainer.innerHTML = '';

  let missionKey = "weather";
  if (currentPromptData) {
    const sc = currentPromptData.scenario_id || "";
    if (sc.includes("restaurant")) missionKey = "restaurant";
    else if (sc.includes("hotel")) missionKey = "hotel";
    else if (sc.includes("opinion")) missionKey = "opinion";
  }

  const mData = MISSIONS_DB[missionKey] || MISSIONS_DB["weather"];
  const langData = targetLanguage === 'es' ? mData.es : mData.ja;

  // Render Choice Chips
  langData.options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'chip-btn';
    btn.innerHTML = `<span>💬 ${opt.text}</span><span class="subtext">(${opt.zh})</span>`;
    btn.onclick = () => {
      document.getElementById('user-input').value = opt.text;
      document.getElementById('user-input').focus();
    };
    optContainer.appendChild(btn);
  });

  // Render Word Chips with Native Meanings
  langData.words.forEach(item => {
    const chip = document.createElement('button');
    chip.className = 'word-chip';
    chip.innerHTML = `<span>+ ${item.w}</span><span class="chip-meaning">(${item.m})</span>`;
    chip.onclick = () => {
      const input = document.getElementById('user-input');
      input.value = (input.value ? input.value + ' ' : '') + item.w;
      input.focus();
    };
    wordContainer.appendChild(chip);
  });
}

function clearInput() {
  document.getElementById('user-input').value = '';
  document.getElementById('user-input').focus();
}

async function loadNextTurn() {
  turnStartTime = Date.now();
  const res = await fetch(apiUrl('api/session/next-turn'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: currentLearnerId, target_language: targetLanguage })
  });
  const data = await res.json();
  currentPromptData = data;

  const chat = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble ai';
  bubble.innerHTML = `
    <div>
      <strong>${data.prompt_target_lang}</strong>
      <button class="sound-btn" onclick="speakText('${data.prompt_target_lang}')" title="點擊發音 🔊">🔊</button>
    </div>
    <div class="trans">${data.prompt_en}</div>
    <div class="meta-tag">🎯 Target: ${data.target_skills.join(', ')}</div>
    ${data.hints ? `<div style="font-size:0.75rem; color:#f59e0b; margin-top:0.35rem;">💡 ${data.hints}</div>` : ''}
  `;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;

  renderScaffolding(data.prompt_target_lang);
  document.getElementById('user-input').focus();
}

function handleKeyPress(event) {
  if (event.key === 'Enter') submitResponse();
}

async function submitResponse() {
  const input = document.getElementById('user-input');
  let text = input.value.trim();
  if (!text) return;

  // Chinese / Native intent translation bridge for beginners
  const isChinese = /[\u4e00-\u9fa5]/.test(text) && !/[\u3040-\u309f\u30a0-\u30ff]/.test(text);
  if (isChinese) {
    if (targetLanguage === 'es') {
      if (text.includes("不去") || text.includes("不出門")) {
        text = "Si llueve mañana, no saldré.";
      } else if (text.includes("吃") || text.includes("拉麵")) {
        text = "Quiero comer ramen.";
      } else if (text.includes("水")) {
        text = "Un vaso de agua, por favor.";
      } else if (text.includes("去過")) {
        text = "Sí, he estado en Japón.";
      } else {
        text = "Sí, por favor.";
      }
    } else {
      if (text.includes("不去") || text.includes("不出門")) {
        text = "明日雨が降ったら、行きません。";
      } else if (text.includes("吃") || text.includes("拉麵")) {
        text = "ラーメンを食べたいです。";
      } else if (text.includes("水")) {
        text = "お水をください。";
      } else if (text.includes("去過")) {
        text = "日本に行ったことがあります。";
      } else {
        text = "はい、そうです。";
      }
    }
  }

  const latency = Date.now() - turnStartTime;
  input.value = '';

  const chat = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble user';
  bubble.innerHTML = `
    <div>${text} <button class="sound-btn" style="color:#fff;" onclick="speakText('${text}')" title="點擊發音 🔊">🔊</button></div>
  `;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;

  const res = await fetch(apiUrl('api/session/submit'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: currentLearnerId, target_language: targetLanguage, response_text: text, latency_ms: latency })
  });
  const data = await res.json();

  document.getElementById('stat-latency').innerText = `${Math.round(data.analysis.latency_ms)} ms`;
  document.getElementById('stat-grammar').innerText = `${Math.round(data.analysis.grammar_accuracy * 100)}%`;
  document.getElementById('stat-semantic').innerText = `${Math.round(data.analysis.semantic_correctness * 100)}%`;
  document.getElementById('stat-natural').innerText = `${Math.round(data.analysis.naturalness * 100)}%`;

  document.getElementById('ir-tree-display').innerText = JSON.stringify(data.analysis.parsed_ir, null, 2);
}

async function testIRTransform() {
  const text = document.getElementById('sandbox-input').value;
  let srcLang = 'en';
  if (/[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf]/.test(text)) {
    srcLang = 'ja';
  } else if (/(\bsi\b|\bquiero\b|\bpor favor\b|\bhe estado\b|\bgracias\b)/i.test(text)) {
    srcLang = 'es';
  }

  const res = await fetch(apiUrl('api/transform'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_language: srcLang, text_or_json: text, target_language: 'ir' })
  });
  const data = await res.json();
  document.getElementById('sandbox-ja').innerText = data.japanese || '--';
  document.getElementById('sandbox-es').innerText = data.spanish || '--';
  document.getElementById('sandbox-en').innerText = data.english || '--';
  document.getElementById('sandbox-ir').innerText = JSON.stringify(data.ir, null, 2);
}

async function loadSkills() {
  const res = await fetch(apiUrl('api/skills'));
  const data = await res.json();
  const container = document.getElementById('skills-container');
  container.innerHTML = '';

  data.universal_skills.forEach(u => {
    const card = document.createElement('div');
    card.className = 'skill-node';
    const jaMappings = data.language_skills.filter(l => l.concept === u.concept && l.language === 'ja');
    const esMappings = data.language_skills.filter(l => l.concept === u.concept && l.language === 'es');

    card.innerHTML = `
      <div class="skill-id">[${u.skill_id}]</div>
      <div style="font-weight:600; color:#fff;">${u.concept} - ${u.description}</div>
      <div style="font-size:0.8rem; color:#94a3b8;">Utility: ${u.communication_utility} | Unlock: ${u.unlock_value}</div>
      <div style="margin-top:0.4rem; display:flex; flex-wrap:wrap; gap:0.3rem;">
        ${jaMappings.map(m => `<span class="message-bubble ai" style="display:inline-block; padding:0.15rem 0.4rem; font-size:0.75rem;">🇯🇵 ${m.realization}</span>`).join('')}
        ${esMappings.map(m => `<span class="message-bubble ai" style="display:inline-block; padding:0.15rem 0.4rem; font-size:0.75rem; border-color:rgba(255,184,0,0.4); color:#fbbf24;">🇪🇸 ${m.realization}</span>`).join('')}
      </div>
    `;
    container.appendChild(card);
  });
}

async function loadProgress() {
  const res = await fetch(apiUrl(`api/progress/${currentLearnerId}?target_language=${targetLanguage}`));
  const data = await res.json();
  const d = data.dimensions;

  document.getElementById('rad-overall').innerText = `${Math.round(data.overall * 100)}%`;
  document.getElementById('bar-overall').style.width = `${Math.round(data.overall * 100)}%`;

  document.getElementById('rad-prod').innerText = `${Math.round(d.production * 100)}%`;
  document.getElementById('bar-prod').style.width = `${Math.round(d.production * 100)}%`;

  document.getElementById('rad-rec').innerText = `${Math.round(d.recognition * 100)}%`;
  document.getElementById('bar-rec').style.width = `${Math.round(d.recognition * 100)}%`;

  document.getElementById('rad-auto').innerText = `${Math.round(d.automaticity * 100)}%`;
  document.getElementById('bar-auto').style.width = `${Math.round(d.automaticity * 100)}%`;

  document.getElementById('rad-ret').innerText = `${Math.round(d.retention * 100)}%`;
  document.getElementById('bar-ret').style.width = `${Math.round(d.retention * 100)}%`;
}

async function runSim(turns) {
  const out = document.getElementById('sim-output');
  out.innerText = `Running ${turns}-turn adaptive learning simulation (${targetLanguage.toUpperCase()})...\n`;
  const res = await fetch(apiUrl('api/simulation/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: 'sim_runner', target_language: targetLanguage, turns: turns })
  });
  const data = await res.json();
  out.innerText = `✅ Simulation Completed (${data.turns_completed} turns):\n\n` + JSON.stringify(data.history, null, 2);
}

window.addEventListener('DOMContentLoaded', () => {
  loadNextTurn();
  testIRTransform();
});
