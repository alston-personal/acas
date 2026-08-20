// ACAS Web Client Logic
let turnStartTime = Date.now();
let currentLearnerId = "web_user";
let targetLanguage = "ja";
let isBeginnerMode = true;
let currentPromptData = null;

const API_BASE = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return API_BASE + cleanPath;
}

function changeTargetLanguage(lang) {
  targetLanguage = lang;
  const labelMap = { ja: "🇯🇵 日語", es: "🇪🇸 西班牙語", en: "🇬🇧 英語" };
  document.getElementById('current-lang-display').innerText = labelMap[lang] || lang;
  
  // Clear chat and reload turn for new language
  document.getElementById('chat-messages').innerHTML = '';
  loadNextTurn();
  loadProgress();
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
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }
}

// Scaffolding database for JA & ES
const SCAFFOLDING_JA = {
  "明日雨が降ったら": {
    options: [
      { text: "明日雨が降ったら、行きません。", zh: "如果明天下雨，我就不去。" },
      { text: "明日雨が降ったら、家で休みます。", zh: "如果明天下雨，就在家休息。" },
      { text: "雨だったら、出かけない。", zh: "如果下雨就不出門 (常體)。" }
    ],
    words: ["明日", "雨が降ったら", "東京に", "行きません", "出かけない", "家で", "休みます", "映画を", "見ます"]
  },
  "住むなら": {
    options: [
      { text: "東京に住みたいです。", zh: "我想住在東京。" },
      { text: "京都に住みたいです。", zh: "我想住在京都。" },
      { text: "日本に住むなら、東京がいいです。", zh: "如果住日本，東京挺好的。" }
    ],
    words: ["東京に", "京都に", "日本に", "住みたいです", "住みたい", "がいいです", "行きたいです"]
  },
  "注文": {
    options: [
      { text: "ラーメンをください。", zh: "請給我一碗拉麵。" },
      { text: "ラーメンが食べたいです。", zh: "我想吃拉麵。" },
      { text: "メニューを見せてください。", zh: "請讓我看一下菜單。" }
    ],
    words: ["ラーメンを", "お水を", "メニューを", "ください", "お願いします", "食べたいです", "飲みたいです"]
  }
};

const SCAFFOLDING_ES = {
  "llueve": {
    options: [
      { text: "Si llueve mañana, no saldré.", zh: "如果明天下雨，我就不出門。" },
      { text: "Si llueve, me quedo en casa.", zh: "如果下雨，我就待在家。" },
      { text: "No voy si llueve.", zh: "如果下雨我不會去。" }
    ],
    words: ["Si", "llueve", "mañana,", "no", "saldré", "voy", "me", "quedo", "en casa", "a Tokio"]
  },
  "pedir": {
    options: [
      { text: "Quiero comer ramen.", zh: "我想吃拉麵。" },
      { text: "Un vaso de agua, por favor.", zh: "請給我一杯水。" },
      { text: "El menú, por favor.", zh: "請給我菜單。" }
    ],
    words: ["Quiero", "comer", "ramen", "Un vaso de agua,", "El menú,", "por favor", "tomar"]
  },
  "reserva": {
    options: [
      { text: "Tengo una reserva a nombre de Tanaka.", zh: "我有一筆以 Tanaka 名義的預約。" },
      { text: "Sí, tengo una reserva.", zh: "是的，我有預約。" }
    ],
    words: ["Tengo", "una", "reserva", "a nombre de", "Sí,", "muchas gracias"]
  },
  "japón": {
    options: [
      { text: "Sí, he estado en Japón.", zh: "有，我曾經去過日本。" },
      { text: "No, nunca he estado allí.", zh: "沒有，我從未去過那裡。" }
    ],
    words: ["Sí,", "No,", "he estado", "en Japón", "en Tokio", "nunca", "me gusta"]
  }
};

function renderScaffolding(promptText) {
  const optContainer = document.getElementById('quick-options-container');
  const wordContainer = document.getElementById('word-chips-container');
  optContainer.innerHTML = '';
  wordContainer.innerHTML = '';

  const db = targetLanguage === 'es' ? SCAFFOLDING_ES : SCAFFOLDING_JA;
  let matched = null;

  for (let key in db) {
    if (promptText.toLowerCase().includes(key.toLowerCase())) {
      matched = db[key];
      break;
    }
  }

  if (!matched) {
    if (targetLanguage === 'es') {
      matched = {
        options: [
          { text: "Sí, por favor.", zh: "好的，請。" },
          { text: "No, gracias.", zh: "不用了，謝謝。" },
          { text: "¿Puede ayudarme?", zh: "能幫我一下嗎？" }
        ],
        words: ["Sí", "No", "por favor", "gracias", "quiero", "ayuda", "dónde está"]
      };
    } else {
      matched = {
        options: [
          { text: "はい、そうです。", zh: "是的，沒錯。" },
          { text: "いいえ、違います。", zh: "不，不是的。" },
          { text: "手伝ってください。", zh: "請幫我一下。" }
        ],
        words: ["はい", "いいえ", "お願いします", "ください", "です", "ます", "行きます", "食べます"]
      };
    }
  }

  matched.options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'chip-btn';
    btn.innerHTML = `<span>💬 ${opt.text}</span><span class="subtext">(${opt.zh})</span>`;
    btn.onclick = () => {
      document.getElementById('user-input').value = opt.text;
      document.getElementById('user-input').focus();
    };
    optContainer.appendChild(btn);
  });

  matched.words.forEach(w => {
    const chip = document.createElement('button');
    chip.className = 'word-chip';
    chip.innerText = `+ ${w}`;
    chip.onclick = () => {
      const input = document.getElementById('user-input');
      input.value = (input.value ? input.value + ' ' : '') + w;
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
    ${data.hints ? `<div style="font-size:0.78rem; color:#f59e0b; margin-top:0.4rem;">💡 ${data.hints}</div>` : ''}
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
  if (/[　-〿぀-ゟ゠-ヿ＀-ﾟ一-龯]/.test(text)) {
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
