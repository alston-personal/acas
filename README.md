# ACAS (Adaptive Communication Acquisition System) v0.1
### Universal Communication IR & Memory-Aware Adaptive Learning

ACAS is an intelligent, bidirectional language acquisition framework powered by **Universal Communication IR (Intermediate Representation)**. It strictly decouples human communicative intent from language-specific syntax (`Language A ↔ IR ↔ Language B`), models multidimensional learner mastery (recognition, production, retention, automaticity latency), and optimizes learning progression through a closed-loop adaptive scheduler.

---

## 🌟 Core Architecture Principles

```
Human Intent
    ↕
Universal Communication IR (Language-Independent)
    ↕
Language Adapters (Japanese / English / Chinese)
    ↕
Natural Language
```

1. **Zero Language Contamination in Core**: No `JP_*`, `EN_*`, or `ZH_*` primitives exist in the Universal Core IR schema. All syntax patterns live inside modular Language Adapters.
2. **Multidimensional Mastery Vector**: Mastery is never a simple boolean (`learned = true`). We continuously track `[recognition, listening, production, pronunciation, composition, pragmatics, automaticity, retention]`.
3. **Automaticity via Latency Tracking**: Tracks median response initiation latency (ms). Fluency requires both grammatical accuracy and fast retrieval (< 1800ms).
4. **Adaptive Memory-Aware Scheduler**: Priority combines forgetting risk (adaptive power-law retention decay), communication utility, weakness, and unlock value:
   $$\text{priority} = \text{forgetting\_risk} \times \text{communication\_utility} \times \text{weakness} \times \text{unlock\_value} \times \text{expected\_gain}$$
5. **Simultaneous Training & Assessment**: Every conversational turn emits structured `LearningEvent` items that feed back into the learner's state.

---

## 🧩 20 Universal MVP Skills

| Primitive / Concept | Category | Description | Japanese Realization |
| :--- | :--- | :--- | :--- |
| `CORE.INFORM` | Intent | Factual assertion | `～です / ～ます` |
| `CORE.ASK` | Intent | Question / Elicitation | `～か` |
| `CORE.NEGATION` | Logic | Scope negation | `～ない / ～ません` |
| `CORE.TIME` | Semantic | Temporal orientation | `昨日 / 今日 / 明日` |
| `CORE.LOCATION` | Semantic | Spatial destination | `[場所]に` |
| `CORE.DESIRE` | Semantic | Desire / Preference | `～たい / ～たいです` |
| `CORE.ABILITY` | Semantic | Ability & Potential | `～ことができる / 可能形` |
| `CORE.EXPERIENCE` | Semantic | Past life experience | `～たことがある` |
| `CORE.OPINION` | Epistemic | Subjective belief/view | `～と思う` |
| `CORE.POSSIBILITY` | Epistemic | Probability & uncertainty | `～かもしれない` |
| `CORE.CAUSE` | Logic | Causal explanation | `～から / ～ので` |
| `CORE.CONDITION` | Logic | Hypothetical condition | `～たら / ～なら / ～ば` |
| `CORE.COMPARISON` | Logic | Property comparison | `～より～` |
| `CORE.REQUEST` | Intent | Polite directive | `～てください / ～をください` |
| `CORE.SUGGEST` | Intent | Proposal / Invitation | `～ましょう / ～ませんか` |
| `CORE.AGREE` | Intent | Consensus / Agreement | `そうですね / 同感です` |
| `CORE.DISAGREE` | Intent | Disagreement / Counter | `そうではありません` |
| `CORE.CONFIRM` | Control | Confirmation seeking | `～でしょう / ～よね` |
| `CORE.CLARIFY` | Control | Clarification request | `どういう意味ですか` |
| `CORE.REPAIR` | Control | Conversational repair | `言い直すと...` |

---

## 🚀 Quick Start

### 1. Run Interactive CLI Session
```bash
python3 cli.py interactive
```

### 2. Run Spaced Learning Benchmark (H1-H6 Verification)
```bash
python3 cli.py benchmark --iterations 50
```

### 3. Run Unit Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### 4. Start the Web Dashboard
```bash
python3 run_demo.py
# Open http://localhost:8090 in your browser
```

---

## 🛡️ Logic & Data Separation

- **Code & Logic Repo**: `/home/ubuntu/acas` (symlinked into `agentmanager/workspace/acas`)
- **Data & Memory Repo**: `/home/ubuntu/agent-data/projects/acas/` (`STATUS.md`, `memory/`, `project.yaml`)
