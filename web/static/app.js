// ACAS Modern Client Logic - Multi-Turn Coherent Episodes
let turnStartTime = Date.now();
let currentLearnerId = "guest_user";
let currentUsername = "Guest";
let currentProvider = "local";

let targetLanguage = "es";
let nativeLanguage = "zh-TW";
let currentEpisodeId = "restaurant_tapas";
let currentTurnIndex = 0;
let currentDifficultyLevel = 1;
let currentPromptData = null;

let assembledWords = [];

const API_BASE = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

function apiUrl(path) {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return API_BASE + cleanPath;
}

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

function changeEpisode(epId) {
  currentEpisodeId = epId;
  currentTurnIndex = 0;
  loadNextTurn(false);
}

function changeNativeLanguage(lang) {
  nativeLanguage = lang;
  loadNextTurn(false);
}

function changeTargetLanguage(lang) {
  targetLanguage = lang;
  loadNextTurn(false);
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

// Word assembly handlers
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

// Load Next Turn within the Coherent Story Episode
async function loadNextTurn(advance = true) {
  turnStartTime = Date.now();
  document.getElementById('feedback-banner').style.display = 'none';

  const res = await fetch(apiUrl('api/session/next-turn'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      learner_id: currentLearnerId,
      native_language: nativeLanguage,
      target_language: targetLanguage,
      episode_id: currentEpisodeId,
      advance_turn: advance
    })
  });
  const data = await res.json();
  currentPromptData = data;
  currentEpisodeId = data.episode_id;
  currentTurnIndex = data.turn_index;
  currentDifficultyLevel = data.difficulty_level || 1;

  // Update Episode & Scene Info
  document.getElementById('episode-select').value = data.episode_id;
  document.getElementById('scenario-icon').innerText = data.episode_icon;
  document.getElementById('scenario-title').innerText = data.episode_title;
  document.getElementById('scenario-domain').innerText = `第 ${data.turn_index + 1}/${data.total_turns} 幕`;
  document.getElementById('episode-step-badge').innerText = data.step_title;

  // Prompts
  document.getElementById('prompt-target-text').innerText = data.prompt_target_lang;
  document.getElementById('prompt-native-text').innerText = data.prompt_native_translation;
  document.getElementById('formula-hint').innerText = data.formula;

  // Render Word Bank
  const poolContainer = document.getElementById('word-pool');
  poolContainer.innerHTML = '';
  (data.words || []).forEach((item, index) => {
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
  (data.choices || []).forEach(ch => {
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

async function submitResponse() {
  let text = "";
  if (assembledWords.length > 0) {
    text = assembledWords.map(a => a.word).join(" ");
  } else {
    text = document.getElementById('input-fallback').value.trim();
  }
  if (!text) return;

  const latency = Date.now() - turnStartTime;

  const res = await fetch(apiUrl('api/session/submit'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      learner_id: currentLearnerId,
      native_language: nativeLanguage,
      target_language: targetLanguage,
      episode_id: currentEpisodeId,
      turn_index: currentTurnIndex,
      response_text: text,
      latency_ms: latency,
      prompt_target_lang: currentPromptData ? currentPromptData.prompt_target_lang : '',
      prompt_native_translation: currentPromptData ? currentPromptData.prompt_native_translation : ''
    })
  });
  const data = await res.json();

  const banner = document.getElementById('feedback-banner');
  const isSuccess = data.is_success;

  banner.className = `feedback-banner ${isSuccess ? 'success' : 'error'}`;
  
  if (data.is_episode_completed) {
    document.getElementById('feedback-icon').innerText = '🏆';
    document.getElementById('feedback-title').innerText = '恭喜通關整集情境故事！';
    document.getElementById('feedback-detail').innerText = `已完成全劇本對話！獲得整體熟練度提升，單字庫已同步更新。`;
  } else {
    document.getElementById('feedback-icon').innerText = isSuccess ? '🎉' : '💡';
    document.getElementById('feedback-title').innerText = isSuccess ? '回答精準！' : '可以嘗試調整用詞：';
    document.getElementById('feedback-detail').innerText = `反應延遲: ${Math.round(data.analysis.latency_ms)}ms · 語法準確: ${Math.round(data.analysis.grammar_accuracy * 100)}%`;
  }
  
  banner.style.display = 'block';
  speakText(text);
}

// Notebook Loader
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

// Engine Sandbox & Progress
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
  loadNextTurn(false);
});
