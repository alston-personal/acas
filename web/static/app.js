// ACAS Web Client Logic
let turnStartTime = Date.now();
let currentLearnerId = "web_user";
let isBeginnerMode = true;
let currentPromptData = null;

// Base API URL prefix support (supports both '/' and '/acas/' reverse proxy)
const API_BASE = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return API_BASE + cleanPath;
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

function speakText(text, lang = 'ja-JP') {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }
}

// Scaffolding database for scenarios
const SCAFFOLDING_DB = {
  "明日雨が降ったら": {
    options: [
      { ja: "明日雨が降ったら、行きません。", zh: "如果明天下雨，我就不去。", autoSend: false },
      { ja: "明日雨が降ったら、家で休みます。", zh: "如果明天下雨，就在家休息。", autoSend: false },
      { ja: "雨だったら、出かけない。", zh: "如果下雨就不出門 (常體)。", autoSend: false }
    ],
    words: ["明日", "雨が降ったら", "東京に", "行きません", "出かけない", "家で", "休みます", "映画を", "見ます"]
  },
  "住むなら": {
    options: [
      { ja: "東京に住みたいです。", zh: "我想住在東京。", autoSend: false },
      { ja: "京都に住みたいです。", zh: "我想住在京都。", autoSend: false },
      { ja: "日本に住むなら、東京がいいです。", zh: "如果住日本，東京挺好的。", autoSend: false }
    ],
    words: ["東京に", "京都に", "日本に", "住みたいです", "住みたい", "がいいです", "行きたいです"]
  },
  "注文": {
    options: [
      { ja: "ラーメンをください。", zh: "請給我一碗拉麵。", autoSend: false },
      { ja: "ラーメンが食べたいです。", zh: "我想吃拉麵。", autoSend: false },
      { ja: "メニューを見せてください。", zh: "請讓我看一下菜單。", autoSend: false }
    ],
    words: ["ラーメンを", "お水を", "メニューを", "ください", "お願いします", "食べたいです", "飲みたいです"]
  },
  "お飲み物": {
    options: [
      { ja: "お水をください。", zh: "請給我一杯水。", autoSend: false },
      { ja: "お茶をお願いします。", zh: "麻煩給我一杯茶。", autoSend: false },
      { ja: "結構です。", zh: "不用了，謝謝。", autoSend: false }
    ],
    words: ["お水を", "お茶を", "ビールを", "ください", "お願いします", "結構です"]
  },
  "行ったことがありますか": {
    options: [
      { ja: "はい、日本に行ったことがあります。", zh: "有，我曾經去過日本。", autoSend: false },
      { ja: "いいえ、行ったことがありません。", zh: "沒有，我還沒去過。", autoSend: false }
    ],
    words: ["はい、", "いいえ、", "日本に", "東京に", "行ったことがあります", "行ったことがありません"]
  },
  "どう思いますか": {
    options: [
      { ja: "とても美味しいと思います。", zh: "我覺得非常美味。", autoSend: false },
      { ja: "面白いと思います。", zh: "我覺得很有趣。", autoSend: false }
    ],
    words: ["とても", "美味しいと", "面白いと", "思います", "思わない", "綺麗だと"]
  },
  "駅はどこですか": {
    options: [
      { ja: "駅はあそこです。", zh: "車站在那邊。", autoSend: false },
      { ja: "まっすぐ行ってください。", zh: "請一直往前走。", autoSend: false }
    ],
    words: ["駅は", "あそこです", "あちらです", "まっすぐ", "行ってください", "右です", "左です"]
  }
};

function renderScaffolding(promptText) {
  const optContainer = document.getElementById('quick-options-container');
  const wordContainer = document.getElementById('word-chips-container');
  optContainer.innerHTML = '';
  wordContainer.innerHTML = '';

  let matched = null;
  for (let key in SCAFFOLDING_DB) {
    if (promptText.includes(key)) {
      matched = SCAFFOLDING_DB[key];
      break;
    }
  }

  // Default fallback scaffolding
  if (!matched) {
    matched = {
      options: [
        { ja: "はい、そうです。", zh: "是的，沒錯。", autoSend: false },
        { ja: "いいえ、違います。", zh: "不，不是的。", autoSend: false },
        { ja: "手伝ってください。", zh: "請幫我一下。", autoSend: false }
      ],
      words: ["はい", "いいえ", "お願いします", "ください", "です", "ます", "行きます", "食べます"]
    };
  }

  // Render Option Chips
  matched.options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'chip-btn';
    btn.innerHTML = `<span>💬 ${opt.ja}</span><span class="subtext">(${opt.zh})</span>`;
    btn.onclick = () => {
      document.getElementById('user-input').value = opt.ja;
      document.getElementById('user-input').focus();
    };
    optContainer.appendChild(btn);
  });

  // Render Word Chips for Sentence Building
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
    body: JSON.stringify({ learner_id: currentLearnerId })
  });
  const data = await res.json();
  currentPromptData = data;

  const chat = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble ai';
  bubble.innerHTML = `
    <div>
      <strong>${data.prompt_ja}</strong>
      <button class="sound-btn" onclick="speakText('${data.prompt_ja}')" title="點擊發音 🔊">🔊</button>
    </div>
    <div class="trans">${data.prompt_en}</div>
    <div class="meta-tag">🎯 Target: ${data.target_skills.join(', ')}</div>
    ${data.hints ? `<div style="font-size:0.78rem; color:#f59e0b; margin-top:0.4rem;">💡 ${data.hints}</div>` : ''}
  `;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;

  // Render Beginner Scaffolding Chips
  renderScaffolding(data.prompt_ja);

  document.getElementById('user-input').focus();
}

function handleKeyPress(event) {
  if (event.key === 'Enter') submitResponse();
}

async function submitResponse() {
  const input = document.getElementById('user-input');
  let text = input.value.trim();
  if (!text) return;

  // Check if user input is Chinese (Beginner Intent translation)
  const isChinese = /[一-龥]/.test(text) && !/[぀-ゟ゠-ヿ]/.test(text);
  if (isChinese) {
    // Map Chinese intent to Japanese realization automatically
    if (text.includes("不去") || text.includes("不出門")) {
      text = "明日雨が降ったら、行きません。";
    } else if (text.includes("東京") || text.includes("住")) {
      text = "東京に住みたいです。";
    } else if (text.includes("拉麵") || text.includes("吃")) {
      text = "ラーメンを食べたいです。";
    } else if (text.includes("水")) {
      text = "お水をください。";
    } else if (text.includes("菜單")) {
      text = "メニューをください。";
    } else if (text.includes("去過")) {
      text = "日本に行ったことがあります。";
    } else {
      text = "はい、そうです。";
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
    body: JSON.stringify({ learner_id: currentLearnerId, response_text: text, latency_ms: latency })
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
  const isJa = /[　-〿぀-ゟ゠-ヿ＀-ﾟ一-龯]/.test(text);
  const srcLang = isJa ? 'ja' : 'en';

  const res = await fetch(apiUrl('api/transform'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_language: srcLang, text_or_json: text, target_language: 'ir' })
  });
  const data = await res.json();
  document.getElementById('sandbox-ja').innerText = data.japanese;
  document.getElementById('sandbox-en').innerText = data.english;
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
    const mappings = data.language_skills.filter(l => l.concept === u.concept);
    card.innerHTML = `
      <div class="skill-id">[${u.skill_id}]</div>
      <div style="font-weight:600; color:#fff;">${u.concept} - ${u.description}</div>
      <div style="font-size:0.8rem; color:#94a3b8;">Utility: ${u.communication_utility} | Dependencies: ${u.dependencies.join(', ') || 'None'}</div>
      <div style="margin-top:0.5rem;">
        ${mappings.map(m => `<span class="message-bubble ai" style="display:inline-block; padding:0.2rem 0.5rem; font-size:0.75rem; margin-right:0.3rem;">🇯🇵 ${m.realization}</span>`).join('')}
      </div>
    `;
    container.appendChild(card);
  });
}

async function loadProgress() {
  const res = await fetch(apiUrl(`api/progress/${currentLearnerId}`));
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
  out.innerText = `Running ${turns}-turn adaptive learning simulation...\n`;
  const res = await fetch(apiUrl('api/simulation/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: 'sim_runner', turns: turns })
  });
  const data = await res.json();
  out.innerText = `✅ Simulation Completed (${data.turns_completed} turns):\n\n` + JSON.stringify(data.history, null, 2);
}

window.addEventListener('DOMContentLoaded', () => {
  loadNextTurn();
  testIRTransform();
});
