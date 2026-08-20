// ACAS Web Client Logic
let turnStartTime = Date.now();
let currentLearnerId = "web_user";

function switchTab(tabId) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  event.target.classList.add('active');

  if (tabId === 'skills-tab') loadSkills();
  if (tabId === 'analytics-tab') loadProgress();
}

async function loadNextTurn() {
  turnStartTime = Date.now();
  const res = await fetch('/api/session/next-turn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ learner_id: currentLearnerId })
  });
  const data = await res.json();

  const chat = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble ai';
  bubble.innerHTML = `
    <div><strong>${data.prompt_ja}</strong></div>
    <div class="trans">${data.prompt_en}</div>
    <div class="meta-tag">🎯 Target: ${data.target_skills.join(', ')}</div>
    ${data.hints ? `<div style="font-size:0.75rem; color:#94a3b8; margin-top:0.3rem;">💡 ${data.hints}</div>` : ''}
  `;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;

  document.getElementById('user-input').focus();
}

function handleKeyPress(event) {
  if (event.key === 'Enter') submitResponse();
}

async function submitResponse() {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;

  const latency = Date.now() - turnStartTime;
  input.value = '';

  const chat = document.getElementById('chat-messages');
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble user';
  bubble.innerText = text;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;

  const res = await fetch('/api/session/submit', {
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
  const isJa = /[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf]/.test(text);
  const srcLang = isJa ? 'ja' : 'en';

  const res = await fetch('/api/transform', {
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
  const res = await fetch('/api/skills');
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
  const res = await fetch(`/api/progress/${currentLearnerId}`);
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
  const res = await fetch('/api/simulation/run', {
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
