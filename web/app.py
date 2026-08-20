"""
ACAS Web API Application

FastAPI Backend supporting Multi-Turn Coherent Scenario Episodes (SLA Contextual Continuity).
"""

import os
import json
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path

from engine.session import ACASSessionEngine
from core.skill_graph import global_skill_graph
from core.validator import IRValidator
from core.ir_schema import CommunicationIR
from core.conversation_generator import GeneratedPrompt
from scenarios.registry import global_scenario_registry
from languages.ja.adapter import JapaneseAdapter
from languages.en.adapter import EnglishAdapter
from languages.es.adapter import SpanishAdapter

app = FastAPI(title="ACAS Universal Communication IR Learning System", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("/home/ubuntu/agent-data/projects/acas/learners")
DATA_DIR.mkdir(parents=True, exist_ok=True)

engines: Dict[str, ACASSessionEngine] = {}
ja_adapter = JapaneseAdapter()
en_adapter = EnglishAdapter()
es_adapter = SpanishAdapter()


def get_user_storage_path(learner_id: str) -> Path:
    clean_id = "".join(c for c in learner_id if c.isalnum() or c in ("-", "_", "@", "."))
    return DATA_DIR / f"{clean_id}.json"


def load_user_notebook(learner_id: str) -> Dict[str, Any]:
    p = get_user_storage_path(learner_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "learner_id": learner_id,
        "vocabulary_bank": {},
        "sentence_history": [],
        "active_episode_id": "restaurant_tapas",
        "active_turn_index": 0,
        "created_at": time.time(),
        "updated_at": time.time(),
    }


def save_user_notebook(learner_id: str, data: Dict[str, Any]):
    p = get_user_storage_path(learner_id)
    data["updated_at"] = time.time()
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_engine(learner_id: str = "web_user", native_language: str = "zh-TW", target_language: str = "es") -> ACASSessionEngine:
    key = f"{learner_id}_{native_language}_{target_language}"
    if key not in engines:
        engine = ACASSessionEngine(learner_id=learner_id)
        engine.profile.native_language = native_language
        engine.profile.target_language = target_language
        engine.goal.language = target_language
        if target_language == "es":
            engine.analyzer.adapter = es_adapter
        elif target_language == "ja":
            engine.analyzer.adapter = ja_adapter
        else:
            engine.analyzer.adapter = en_adapter
        engines[key] = engine
    return engines[key]


class NextTurnRequest(BaseModel):
    learner_id: str = "web_user"
    native_language: str = "zh-TW"
    target_language: str = "es"
    episode_id: Optional[str] = None
    advance_turn: bool = True


class SubmitResponseRequest(BaseModel):
    learner_id: str = "web_user"
    native_language: str = "zh-TW"
    target_language: str = "es"
    episode_id: str = "restaurant_tapas"
    turn_index: int = 0
    response_text: str
    latency_ms: float
    prompt_target_lang: Optional[str] = None
    prompt_native_translation: Optional[str] = None


class IRTransformRequest(BaseModel):
    source_language: str
    text_or_json: str
    target_language: str


class SimulationRequest(BaseModel):
    learner_id: str = "sim_user"
    target_language: str = "es"
    turns: int = 15


@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "0.1", "system": "ACAS Universal Communication IR"}


@app.get("/api/episodes")
def get_episodes(native_language: str = "zh-TW"):
    episodes = []
    for ep in global_scenario_registry.list_all():
        episodes.append({
            "episode_id": ep.episode_id,
            "icon": ep.icon,
            "domain": ep.domain,
            "title": ep.title_native.get(native_language, ep.title_native.get("zh-TW", "")),
            "description": ep.description_native.get(native_language, ep.description_native.get("zh-TW", "")),
            "total_turns": len(ep.turns),
        })
    return {"episodes": episodes}


@app.get("/api/notebook/{learner_id}")
def get_notebook(learner_id: str):
    return load_user_notebook(learner_id)


@app.get("/api/progress/{learner_id}")
def get_progress(learner_id: str, native_language: str = "zh-TW", target_language: str = "es"):
    engine = get_engine(learner_id, native_language=native_language, target_language=target_language)
    prog = engine.compute_progress()
    notebook = load_user_notebook(learner_id)

    return {
        "goal_id": prog.goal_id,
        "native_language": native_language,
        "target_language": target_language,
        "difficulty_level": engine.profile.current_difficulty_level,
        "consecutive_correct": engine.profile.consecutive_global_correct,
        "overall": prog.overall,
        "dimensions": prog.dimensions.model_dump(),
        "vocabulary_count": len(notebook.get("vocabulary_bank", {})),
        "sentences_practiced_count": len(notebook.get("sentence_history", [])),
    }


@app.post("/api/session/next-turn")
def next_turn(req: NextTurnRequest):
    engine = get_engine(req.learner_id, native_language=req.native_language, target_language=req.target_language)
    notebook = load_user_notebook(req.learner_id)

    # Determine episode
    chosen_ep_id = req.episode_id or notebook.get("active_episode_id", "restaurant_tapas")
    episode = global_scenario_registry.get(chosen_ep_id) or global_scenario_registry.list_all()[0]

    # Determine turn inside episode
    current_turn_idx = notebook.get("active_turn_index", 0)
    if req.advance_turn:
        current_turn_idx = (current_turn_idx) % len(episode.turns)

    turn = episode.turns[current_turn_idx]
    engine.session_turn_count += 1

    prompt_target = turn.prompts_target.get(req.target_language, turn.prompts_target.get("es", ""))
    trans_native = turn.translations_native.get(req.native_language, turn.translations_native.get("zh-TW", ""))
    hints_native = turn.hints_native.get(req.native_language, turn.hints_native.get("zh-TW", ""))
    step_title = turn.step_title.get(req.native_language, turn.step_title.get("zh-TW", f"第 {current_turn_idx+1} 幕"))
    
    target_skills = turn.target_skills_by_lang.get(req.target_language, turn.target_skills_universal)
    formula = turn.formula.get(req.target_language, turn.formula.get("es", ""))
    choices = turn.choices_by_lang.get(req.target_language, turn.choices_by_lang.get("es", []))
    words = turn.words_by_lang.get(req.target_language, turn.words_by_lang.get("es", []))

    # Set engine active prompt to guarantee process_response works
    engine.current_prompt = GeneratedPrompt(
        scenario_id=episode.episode_id,
        domain=episode.domain,
        turn_index=current_turn_idx + 1,
        prompt_text_ja=prompt_target,
        prompt_text_en=trans_native,
        target_skills=target_skills,
        hints=hints_native,
        expected_ir={},
    )

    return {
        "episode_id": episode.episode_id,
        "episode_title": episode.title_native.get(req.native_language, episode.title_native.get("zh-TW", "")),
        "episode_icon": episode.icon,
        "turn_index": current_turn_idx,
        "total_turns": len(episode.turns),
        "step_title": step_title,
        "native_language": req.native_language,
        "target_language": req.target_language,
        "difficulty_level": engine.profile.current_difficulty_level,
        "prompt_target_lang": prompt_target,
        "prompt_native_translation": trans_native,
        "hints_native": hints_native,
        "formula": formula,
        "target_skills": target_skills,
        "choices": choices,
        "words": words,
    }


@app.post("/api/session/submit")
def submit_response(req: SubmitResponseRequest):
    engine = get_engine(req.learner_id, native_language=req.native_language, target_language=req.target_language)
    episode = global_scenario_registry.get(req.episode_id) or global_scenario_registry.list_all()[0]
    turn = episode.turns[req.turn_index % len(episode.turns)]
    target_skills = turn.target_skills_by_lang.get(req.target_language, turn.target_skills_universal)

    # Always ensure active prompt exists
    if not engine.current_prompt:
        engine.current_prompt = GeneratedPrompt(
            scenario_id=episode.episode_id,
            domain=episode.domain,
            turn_index=req.turn_index + 1,
            prompt_text_ja=req.prompt_target_lang or turn.prompts_target.get(req.target_language, ""),
            prompt_text_en=req.prompt_native_translation or "",
            target_skills=target_skills,
            hints="",
            expected_ir={},
        )

    analysis = engine.process_response(req.response_text, req.latency_ms)
    
    is_success = (analysis.grammar_accuracy >= 0.65)
    engine.profile.update_adaptive_difficulty(is_success)

    notebook = load_user_notebook(req.learner_id)

    # Advance to next turn in story on success
    if is_success:
        notebook["active_turn_index"] = (req.turn_index + 1) % len(episode.turns)
        notebook["active_episode_id"] = req.episode_id
    
    # Record history
    sentence_entry = {
        "timestamp": time.time(),
        "episode_id": req.episode_id,
        "target_language": req.target_language,
        "prompt_target": req.prompt_target_lang or turn.prompts_target.get(req.target_language, ""),
        "prompt_native": req.prompt_native_translation or turn.translations_native.get(req.native_language, ""),
        "response_text": req.response_text,
        "latency_ms": req.latency_ms,
        "grammar_accuracy": round(analysis.grammar_accuracy, 2),
        "semantic_correctness": round(analysis.semantic_correctness, 2),
        "naturalness": round(analysis.naturalness, 2),
        "detected_skills": analysis.detected_skills,
        "parsed_ir": analysis.parsed_ir.model_dump() if hasattr(analysis.parsed_ir, 'model_dump') else analysis.parsed_ir,
    }
    notebook["sentence_history"].insert(0, sentence_entry)
    if len(notebook["sentence_history"]) > 100:
        notebook["sentence_history"].pop()

    # Extract words
    tokens = req.response_text.replace("、", " ").replace("。", " ").replace(",", " ").replace(".", " ").replace("¿", " ").replace("?", " ").replace("¡", " ").replace("!", " ").split()
    for w in tokens:
        clean_w = w.strip()
        if len(clean_w) > 1:
            if clean_w not in notebook["vocabulary_bank"]:
                notebook["vocabulary_bank"][clean_w] = {
                    "word": clean_w,
                    "language": req.target_language,
                    "count": 0,
                    "last_seen": time.time(),
                    "mastery_score": 0.5,
                }
            notebook["vocabulary_bank"][clean_w]["count"] += 1
            notebook["vocabulary_bank"][clean_w]["last_seen"] = time.time()
            if is_success:
                notebook["vocabulary_bank"][clean_w]["mastery_score"] = min(1.0, notebook["vocabulary_bank"][clean_w]["mastery_score"] + 0.1)

    save_user_notebook(req.learner_id, notebook)
    progress = engine.compute_progress()

    is_episode_completed = (is_success and req.turn_index == len(episode.turns) - 1)

    return {
        "analysis": {
            "semantic_correctness": round(analysis.semantic_correctness, 2),
            "grammar_accuracy": round(analysis.grammar_accuracy, 2),
            "naturalness": round(analysis.naturalness, 2),
            "pragmatic_appropriateness": round(analysis.pragmatic_appropriateness, 2),
            "detected_skills": analysis.detected_skills,
            "parsed_ir": analysis.parsed_ir.model_dump() if hasattr(analysis.parsed_ir, 'model_dump') else analysis.parsed_ir,
            "latency_ms": req.latency_ms,
        },
        "is_success": is_success,
        "is_episode_completed": is_episode_completed,
        "next_turn_index": notebook["active_turn_index"],
        "difficulty_level": engine.profile.current_difficulty_level,
        "consecutive_correct": engine.profile.consecutive_global_correct,
        "progress": progress.model_dump(),
    }


@app.post("/api/transform")
def transform_ir(req: IRTransformRequest):
    try:
        if req.source_language == "ja":
            ir = ja_adapter.parse(req.text_or_json)
        elif req.source_language == "en":
            ir = en_adapter.parse(req.text_or_json)
        elif req.source_language == "es":
            ir = es_adapter.parse(req.text_or_json)
        elif req.source_language == "ir":
            data = json.loads(req.text_or_json)
            ir = CommunicationIR.from_dict(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid source language")

        valid, errors = IRValidator.validate_ir(ir)
        ja_out = ja_adapter.realize(ir)
        en_out = en_adapter.realize(ir)
        es_out = es_adapter.realize(ir)

        return {
            "valid": valid,
            "validation_errors": errors,
            "ir": ir.model_dump(),
            "japanese": ja_out,
            "english": en_out,
            "spanish": es_out,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulation/run")
def run_simulation(req: SimulationRequest):
    engine = get_engine(req.learner_id, target_language=req.target_language)
    
    simulated_responses = [
        ("Sí, tengo una reserva.", 1100.0),
        ("Quiero comer paella.", 1000.0),
        ("Un vaso de agua, por favor.", 750.0),
        ("Creo que es muy deliciosa.", 1200.0),
    ] if req.target_language == "es" else [
        ("はい、予約しています。", 1200.0),
        ("ラーメンを食べたいです。", 1050.0),
        ("お水をください。", 800.0),
        ("とても美味しいと思います。", 1150.0),
    ]

    history = []
    for i in range(req.turns):
        resp, lat = simulated_responses[i % len(simulated_responses)]
        prompt = engine.start_next_turn()
        analysis = engine.process_response(resp, lat)
        is_success = (analysis.grammar_accuracy >= 0.65)
        engine.profile.update_adaptive_difficulty(is_success)
        prog = engine.compute_progress()
        history.append({
            "turn": engine.session_turn_count,
            "target_language": req.target_language,
            "response": resp,
            "latency_ms": lat,
            "overall_mastery": prog.overall,
        })

    return {
        "learner_id": req.learner_id,
        "target_language": req.target_language,
        "turns_completed": len(history),
        "history": history,
        "final_progress": engine.compute_progress().model_dump(),
    }


static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
