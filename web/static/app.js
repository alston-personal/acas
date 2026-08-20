// ACAS Modern Client Logic
let turnStartTime = Date.now();
let currentLearnerId = "guest_user";
let currentUsername = "Guest";
let currentProvider = "local";

let targetLanguage = "es";
let nativeLanguage = "zh-TW";
let currentDifficultyLevel = 1;
let consecutiveCorrect = 0;
let currentPromptData = null;

let assembledWords = [];

const API_BASE = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return API_BASE + cleanPath;
}

// 1. Navigation View Switcher
function switchView(viewId) {
  document.querySelectorAll('.view-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab-btn').forEach(el => el.classList.remove('active'));
  
  document.getElementById(viewId).classList.add('active');
  event.target.classList.add('active');

  if (viewId === 'notebook-view') loadNotebook();
  if (viewId === 'engine-view') {
    testIRTransform();
    loadProgress();
  }
}

// 2. Auth Session Check
async function checkAuthSession() {
  try {
    const res = await fetch('/dashboard/api/auth/session');
    if (res.ok) {
      const data = await res.json();
      if (data.loggedIn && data.username) {
        currentUsername = data.username;
        currentProvider = data.provider || 'portal';
        currentLearnerId = `user_${data.username}`;

        document.getElementById('auth-logged-out').style.display = 'none';
        document.getElementById('auth-logged-in').style.display = 'flex';
        document.getElementById('user-display-name').innerText = `👤 ${data.username}`;
      }
    }
  } catch (e) {
    console.log('Portal auth check failed or standalone mode:', e);
  }
}

function changeNativeLanguage(lang) {
  nativeLanguage = lang;
  loadNextTurn();
}

function changeTargetLanguage(lang) {
  targetLanguage = lang;
  loadNextTurn();
}

function speakText(text, lang) {
  if ('speechSynthesis' in window) {
    const langCode = lang || (targetLanguage === 'es' ? 'es-ES' : (targetLanguage === 'ja' ? 'ja-JP' : 'en-US'));
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.88;
    window.speechSynthesis.speak(utterance);
  }
}

function playCurrentPrompt() {
  if (currentPromptData) {
    speakText(currentPromptData.prompt_target_lang);
  }
}

// 3. Scenario & Assembly Data
const SCENARIO_THEMES = {
  "daily.weather.plan": { icon: "🌦️", title: "天氣計劃與出行", domain: "日常生活" },
  "travel.restaurant.order": { icon: "🍽️", title: "餐廳點餐與需求", domain: "旅遊餐飲" },
  "daily.opinion.chat": { icon: "💬", title: "旅遊經驗與心得", domain: "日常社交" }
};

const PRACTICE_DB = {
  "daily.weather.plan": {
    formula: "[Si 如果] + [llueve 下雨], [no saldré / no voy 我不出門]",
    es: {
      choices: [
        "Si llueve mañana, no saldré.",
        "Si llueve, me quedo en casa.",
        "No voy si llueve mañana."
      ],
      words: [
        { w: "Si", m: "如果" }, { w: "llueve", m: "下雨" }, { w: "mañana,", m: "明天" },
        { w: "no", m: "不" }, { w: "saldré", m: "出門" }, { w: "voy", m: "去" },
        { w: "me quedo", m: "待在" }, { w: "en casa", m: "家裡" }
      ]
    },
    ja: {
      choices: [
        "明日雨が降ったら、行きません。",
        "明日雨が降ったら、家で休みます。",
        "雨だったら、出かけない。"
      ],
      words: [
        { w: "明日", m: "明天" }, { w: "雨が降ったら", m: "如果下雨" },
        { w: "行きません", m: "不去" }, { w: "出かけない", m: "不出門" },
        { w: "家で", m: "在家" }, { w: "休みます", m: "休息" }
      ]
    },
    en: {
      choices: [
        "If it rains tomorrow, I will not go out.",
        "If it rains, I will stay at home."
      ],
      words: [
        { w: "If", m: "如果" }, { w: "it rains", m: "下雨" }, { w: "tomorrow,", m: "明天" },
        { w: "I will not", m: "我將不" }, { w: "go out", m: "出門" }
      ]
    }
  },
  "travel.restaurant.order": {
    formula: "[Quiero 想吃] + [ramen 拉麵] / [Un vaso de agua 一杯水], [por favor 請]",
    es: {
      choices: [
        "Quiero comer ramen.",
        "Un vaso de agua, por favor.",
        "El menú, por favor."
      ],
      words: [
        { w: "Quiero", m: "我想要" }, { w: "comer", m: "吃" }, { w: "ramen", m: "拉麵" },
        { w: "Un vaso de agua,", m: "一杯水" }, { w: "El menú,", m: "菜單" }, { w: "por favor", m: "請" }
      ]
    },
    ja: {
      choices: [
        "ラーメンをください。",
        "ラーメンが食べたいです。",
        "お水をください。"
      ],
      words: [
        { w: "ラーメンを", m: "拉麵" }, { w: "お水を", m: "水" }, { w: "メニューを", m: "菜單" },
        { w: "ください", m: "請給我" }, { w: "食べたいです", m: "想吃" }
      ]
    },
    en: {
      choices: [
        "I want to eat ramen.",
        "A glass of water, please."
      ],
      words: [
        { w: "I want", m: "我想要" }, { w: "to eat", m: "吃" }, { w: "ramen", m: "拉麵" },
        { w: "water,", m: "水" }, { w: "please", m: "請" }
      ]
    }
  },
  "daily.opinion.chat": {
    formula: "[Creo que 我覺得] + [es muy delicioso 非常美味]",
    es: {
      choices: [
        "Sí, he estado en Japón.",
        "Creo que es muy delicioso."
      ],
      words: [
        { w: "Sí,", m: "有/是的" }, { w: "he estado", m: "我曾去過" }, { w: "en Japón", m: "在日本" },
        { w: "Creo que", m: "我覺得" }, { w: "es muy delicioso", m: "非常美味" }
      ]
    },
    ja: {
      choices: [
        "はい、日本に行ったことがあります。",
        "とても美味しいと思います。"
      ],
      words: [
        { w: "はい、", m: "是的" }, { w: "日本に", m: "去日本" }, { w: "行ったことがあります", m: "曾經去過" },
        { w: "とても美味しいと", m: "非常美味" }, { w: "思います", m: "我覺得" }
      ]
    },
    en: {
      choices: [
        "Yes, I have been to Japan.",
        "I think it is very delicious."
      ],
      words: [
        { w: "Yes,", m: "是的" }, { w: "I have been", m: "我曾去過" }, { w: "to Japan", m: "去日本" },
        { w: "I think", m: "我覺得" }, { w: "delicious", m: "美味" }
      ]
    }
  }
};

// 4. Interactive Word Assembly Engine
function renderAssemblyArea(scenarioId) {
  const pData = PRACTICE_DB[scenarioId] || PRACTICE_DB["daily.weather.plan"];
  const langData = pData[targetLanguage] || pData["es"];

  document.getElementById('formula-hint').innerText = pData.formula;

  // Render Word Pool
  const poolContainer = document.getElementById('word-pool');
  poolContainer.innerHTML = '';
  langData.words.forEach((item, index) => {
    const btn = document.createElement('button');
    btn.className = 'chip-block';
    btn.id = `chip-item-${index}`;
    btn.innerHTML = `<span>${item.w}</span><span class="chip-sub">(${item.m})</span>`;
    btn.onclick = () => addWordToSlot(item.w, index);
    poolContainer.appendChild(btn);
  });

  // Render Quick Choices
  const choiceContainer = document.getElementById('quick-choices');
  choiceContainer.innerHTML = '';
  langData.choices.forEach(ch => {
    const chip = document.createElement('button');
    chip.className = 'choice-chip';
    chip.innerText = `💬 ${ch}`;
    chip.onclick = () => {
      clearAssembledWords();
      document.getElementById('input-fallback').value = ch;
      document.getElementById('construction-slots').classList.add('has-items');
    };
    choiceContainer.appendChild(chip);
  });

  clearAssembledWords();
}

function addWordToSlot(word, poolIndex) {
  assembledWords.push({ word, poolIndex });
  renderAssembledSlots();
  const chipEl = document.getElementById(`chip-item-${poolIndex}`);
  if (chipEl) chipEl.classList.add('used');
}

function removeWordFromSlot(slotIndex) {
  const removed = assembledWords.splice(slotIndex, 1)[0];
  renderAssembledSlots();
  if (removed && removed.poolIndex !== undefined) {
    const chipEl = document.getElementById(`chip-item-${removed.poolIndex}`);
    if (chipEl) chipEl.classList.remove('used');
  }
}

function renderAssembledSlots() {
  const container = document.getElementById('assembled-chips-container');
  const slotsWrapper = document.getElementById('construction-slots');
  const fallbackInput = document.getElementById('input-fallback');
  container.innerHTML = '';

  if (assembledWords.length > 0) {
    slotsWrapper.classList.add('has-items');
    fallbackInput.placeholder = '';
    assembledWords.forEach((item, i) => {
      const tag = document.createElement('span');
      tag.className = 'assembled-word';
      tag.innerHTML = `<span>${item.word}</span> <span style="font-size:0.7rem; opacity:0.7;">&times;</span>`;
      tag.onclick = (e) => {
        e.stopPropagation();
        removeWordFromSlot(i);
      };
      container.appendChild(tag);
    });
  } else {
    if (!fallbackInput.value.trim()) {
      slotsWrapper.classList.remove('has-items');
    }
    fallbackInput.placeholder = '點擊積木或在此輸入...';
  }
}

function clearAssembledWords() {
  assembledWords = [];
  document.getElementById('input-fallback').value = '';
  renderAssembledSlots();
  document.querySelectorAll('.chip-block').forEach(el => el.classList.remove('used'));
}

function focusInputFallback() {
  document.getElementById('input-fallback').focus();
}

function handleKeyPress(event) {
  if (event.key === 'Enter') submitResponse();
}

// 5. Turn Loader & Submission
async function loadNextTurn() {
  turnStartTime = Date.now();
  document.getElementById('feedback-banner').style.display = 'none';

  const res = await fetch(apiUrl('api/session/next-turn'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: currentLearnerId, native_language: nativeLanguage, target_language: targetLanguage })
  });
  const data = await res.json();
  currentPromptData = data;
  currentDifficultyLevel = data.difficulty_level || 1;

  // Theme info
  const theme = SCENARIO_THEMES[data.scenario_id] || { icon: "💬", title: "對話練習", domain: "日常" };
  document.getElementById('scenario-icon').innerText = theme.icon;
  document.getElementById('scenario-title').innerText = `情境：${theme.title}`;
  document.getElementById('scenario-domain').innerText = theme.domain;

  // Prompt bubbles
  document.getElementById('prompt-target-text').innerText = data.prompt_target_lang;
  document.getElementById('prompt-native-text').innerText = data.prompt_native_translation;

  // Difficulty badge
  const diffLabels = { 1: "⭐ Level 1: 入門引導", 2: "⭐⭐ Level 2: 積木挑戰", 3: "⭐⭐⭐ Level 3: 直覺盲測" };
  document.getElementById('difficulty-badge').innerText = diffLabels[currentDifficultyLevel] || "⭐ Level 1";

  // Render Assembly zone
  renderAssemblyArea(data.scenario_id);
}

async function submitResponse() {
  let text = "";
  if (assembledWords.length > 0) {
    text = assembledWords.map(a => a.word).join(" ");
  } else {
    text = document.getElementById('input-fallback').value.trim();
  }
  if (!text) return;

  // Chinese intent bridge
  const isChinese = /[\u4e00-\u9fa5]/.test(text) && !/[\u3040-\u309f\u30a0-\u30ff]/.test(text);
  if (isChinese) {
    if (targetLanguage === 'es') {
      if (text.includes("不去") || text.includes("不出門")) text = "Si llueve mañana, no saldré.";
      else if (text.includes("吃") || text.includes("拉麵")) text = "Quiero comer ramen.";
      else text = "Sí, por favor.";
    } else {
      if (text.includes("不去") || text.includes("不出門")) text = "明日雨が降ったら、行きません。";
      else if (text.includes("吃") || text.includes("拉麵")) text = "ラーメンを食べたいです。";
      else text = "はい、そうです。";
    }
  }

  const latency = Date.now() - turnStartTime;

  const res = await fetch(apiUrl('api/session/submit'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      learner_id: currentLearnerId,
      native_language: nativeLanguage,
      target_language: targetLanguage,
      response_text: text,
      latency_ms: latency,
      prompt_target_lang: currentPromptData ? currentPromptData.prompt_target_lang : '',
      prompt_native_translation: currentPromptData ? currentPromptData.prompt_native_translation : ''
    })
  });
  const data = await res.json();

  // Show Feedback Drawer
  const banner = document.getElementById('feedback-banner');
  const isSuccess = (data.analysis.grammar_accuracy >= 0.7);

  banner.className = `feedback-banner ${isSuccess ? 'success' : 'error'}`;
  document.getElementById('feedback-icon').innerText = isSuccess ? '🎉' : '💡';
  document.getElementById('feedback-title').innerText = isSuccess ? '作答正確！' : '請再試一次！';
  document.getElementById('feedback-detail').innerText = `反應延遲: ${Math.round(data.analysis.latency_ms)}ms · 語法吻合: ${Math.round(data.analysis.grammar_accuracy * 100)}% · 意圖: ${data.analysis.parsed_ir.intent?.type || 'INFORM'}`;
  banner.style.display = 'block';

  // Speak user response
  speakText(text);
}

// 6. Notebook Loader
async function loadNotebook() {
  try {
    const res = await fetch(apiUrl(`api/notebook/${currentLearnerId}`));
    const data = await res.json();

    const vocabContainer = document.getElementById('vocab-bank-container');
    const sentContainer = document.getElementById('sentence-history-container');
    vocabContainer.innerHTML = '';
    sentContainer.innerHTML = '';

    const vocabList = Object.values(data.vocabulary_bank || {});
    document.getElementById('notebook-vocab-count').innerText = vocabList.length;
    document.getElementById('notebook-sentence-count').innerText = (data.sentence_history || []).length;

    if (vocabList.length === 0) {
      vocabContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; padding:1.5rem; text-align:center;">尚未收錄單字，開始練習對話即可自動收錄！</div>';
    } else {
      vocabList.forEach(v => {
        const row = document.createElement('div');
        row.className = 'vocab-row';
        row.innerHTML = `
          <div>
            <span style="font-weight:700; color:#fff;">${v.word}</span>
            <button class="btn-audio" style="font-size:0.85rem; margin-left:0.3rem;" onclick="speakText('${v.word}')">🔊</button>
            <div style="font-size:0.7rem; color:var(--text-sub);">練習: ${v.count} 次 · 語言: ${v.language.toUpperCase()}</div>
          </div>
          <div style="color:var(--accent-green); font-size:0.8rem; font-weight:700;">${Math.round(v.mastery_score * 100)}%</div>
        `;
        vocabContainer.appendChild(row);
      });
    }

    const sentences = data.sentence_history || [];
    if (sentences.length === 0) {
      sentContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; padding:1.5rem; text-align:center;">尚未有練習紀錄，前往「互動練習」完成對話即可記錄！</div>';
    } else {
      sentences.forEach(s => {
        const row = document.createElement('div');
        row.className = 'vocab-row';
        row.style.flexDirection = 'column';
        row.style.alignItems = 'flex-start';
        row.style.gap = '0.3rem';
        row.innerHTML = `
          <div style="display:flex; justify-content:space-between; width:100%; font-size:0.75rem; color:var(--text-muted);">
            <span>${new Date(s.timestamp * 1000).toLocaleTimeString()}</span>
            <span style="color:var(--accent-cyan);">準確: ${Math.round(s.grammar_accuracy * 100)}% · 延遲: ${Math.round(s.latency_ms)}ms</span>
          </div>
          <div style="font-size:0.82rem; color:var(--text-sub);">❓ ${s.prompt_target}</div>
          <div style="font-weight:700; color:#fff; display:flex; align-items:center; gap:0.4rem;">
            <span>💬 ${s.response_text}</span>
            <button class="btn-audio" style="font-size:0.85rem;" onclick="speakText('${s.response_text}')">🔊</button>
          </div>
        `;
        sentContainer.appendChild(row);
      });
    }
  } catch (e) {
    console.error('Failed to load notebook:', e);
  }
}

// 7. Engine Sandbox & Progress
async function testIRTransform() {
  const text = document.getElementById('sandbox-input').value;
  let srcLang = 'en';
  if (/[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf]/.test(text)) srcLang = 'ja';
  else if (/(\bsi\b|\bquiero\b|\bpor favor\b|\bhe estado\b|\bgracias\b)/i.test(text)) srcLang = 'es';

  const res = await fetch(apiUrl('api/transform'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_language: srcLang, text_or_json: text, target_language: 'ir' })
  });
  const data = await res.json();
  document.getElementById('sandbox-es').innerText = data.spanish || '--';
  document.getElementById('sandbox-ja').innerText = data.japanese || '--';
  document.getElementById('sandbox-en').innerText = data.english || '--';
  document.getElementById('sandbox-ir').innerText = JSON.stringify(data.ir, null, 2);
}

async function loadProgress() {
  const res = await fetch(apiUrl(`api/progress/${currentLearnerId}?native_language=${nativeLanguage}&target_language=${targetLanguage}`));
  const data = await res.json();
  const d = data.dimensions;

  document.getElementById('rad-overall').innerText = `${Math.round(data.overall * 100)}%`;
  document.getElementById('rad-prod').innerText = `${Math.round(d.production * 100)}%`;
  document.getElementById('rad-rec').innerText = `${Math.round(d.recognition * 100)}%`;
  document.getElementById('rad-auto').innerText = `${Math.round(d.automaticity * 100)}%`;
}

async function runSim(turns) {
  const out = document.getElementById('sim-output');
  out.innerText = `Running ${turns}-turn simulation...\n`;
  const res = await fetch(apiUrl('api/simulation/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: 'sim_runner', target_language: targetLanguage, turns: turns })
  });
  const data = await res.json();
  out.innerText = `✅ Simulation Completed (${data.turns_completed} turns):\n\n` + JSON.stringify(data.history, null, 2);
}

window.addEventListener('DOMContentLoaded', async () => {
  await checkAuthSession();
  loadNextTurn();
});
