"""
ACAS Web API Application

FastAPI Backend providing full endpoints for interactive conversation,
skill graph exploration, IR bidirectional conversion, and learner mastery analytics.
"""

import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from engine.session import ACASSessionEngine
from core.skill_graph import global_skill_graph
from core.validator import IRValidator
from core.ir_schema import CommunicationIR
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

engines: Dict[str, ACASSessionEngine] = {}
ja_adapter = JapaneseAdapter()
en_adapter = EnglishAdapter()
es_adapter = SpanishAdapter()


def get_engine(learner_id: str = "web_user", target_language: str = "ja") -> ACASSessionEngine:
    key = f"{learner_id}_{target_language}"
    if key not in engines:
        engine = ACASSessionEngine(learner_id=learner_id)
        engine.goal.language = target_language
        engine.profile.target_language = target_language
        if target_language == "es":
            engine.analyzer.adapter = es_adapter
        elif target_language == "en":
            engine.analyzer.adapter = en_adapter
        else:
            engine.analyzer.adapter = ja_adapter
        engines[key] = engine
    return engines[key]


class NextTurnRequest(BaseModel):
    learner_id: str = "web_user"
    target_language: str = "ja"
    domain: Optional[str] = None


class SubmitResponseRequest(BaseModel):
    learner_id: str = "web_user"
    target_language: str = "ja"
    response_text: str
    latency_ms: float


class IRTransformRequest(BaseModel):
    source_language: str  # "ja", "en", "es", "ir"
    text_or_json: str
    target_language: str  # "ja", "en", "es", "ir"


class SimulationRequest(BaseModel):
    learner_id: str = "sim_user"
    target_language: str = "ja"
    turns: int = 15


@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "0.1", "system": "ACAS Universal Communication IR", "supported_languages": ["ja", "es", "en"]}


@app.get("/api/skills")
def get_skills():
    universals = [u.model_dump() for u in global_skill_graph.universal_skills.values()]
    languages = [l.model_dump() for l in global_skill_graph.language_skills.values()]
    return {
        "universal_skills": universals,
        "language_skills": languages,
    }


@app.get("/api/progress/{learner_id}")
def get_progress(learner_id: str, target_language: str = "ja"):
    engine = get_engine(learner_id, target_language=target_language)
    prog = engine.compute_progress()
    
    skill_states = {}
    for sid, st in engine.profile.skills.items():
        skill_states[sid] = {
            "mastery": st.mastery.model_dump(),
            "overall": round(st.mastery.overall_mastery, 2),
            "median_latency_ms": round(st.median_latency_ms, 0),
            "stability_days": round(st.memory.stability_days, 2),
            "retrievability": round(st.memory.retrievability, 2),
            "statistics": st.statistics.model_dump(),
            "is_fluent": st.is_fluent(),
        }

    return {
        "goal_id": prog.goal_id,
        "target_language": target_language,
        "overall": prog.overall,
        "dimensions": prog.dimensions.model_dump(),
        "mastered_skills_count": prog.mastered_skills_count,
        "total_skills_count": prog.total_skills_count,
        "skill_states": skill_states,
        "total_events": len(engine.event_store.get_all_events()),
    }


@app.post("/api/session/next-turn")
def next_turn(req: NextTurnRequest):
    engine = get_engine(req.learner_id, target_language=req.target_language)
    prompt = engine.start_next_turn(domain=req.domain)
    cluster = engine.current_cluster
    
    # Adapt prompt text based on target language
    if req.target_language == "es":
        # Spanish prompts
        es_prompts = {
            "daily.weather.plan": ("Si llueve mañana, ¿qué vas a hacer?", "¿Qué quieres hacer si llueve mañana?"),
            "travel.restaurant.order": ("¡Bienvenido! ¿Qué desea pedir?", "¿Qué desea tomar?"),
            "travel.hotel.checkin": ("Buenas tardes. ¿Tiene una reserva?", "¿Puede decirme su nombre?"),
            "daily.opinion.chat": ("¿Ha estado en Japón alguna vez?", "¿Qué piensa del ramen?"),
            "travel.direction.ask": ("Disculpe, ¿dónde está la estación?", "¿Cómo puedo llegar allí?"),
        }
        p_text, _ = es_prompts.get(prompt.scenario_id, ("Si llueve mañana, ¿qué vas a hacer?", "Welcome"))
        display_prompt = p_text
    else:
        display_prompt = prompt.prompt_text_ja

    return {
        "turn_count": engine.session_turn_count,
        "scenario_id": prompt.scenario_id,
        "domain": prompt.domain,
        "target_language": req.target_language,
        "prompt_target_lang": display_prompt,
        "prompt_en": prompt.prompt_text_en,
        "target_skills": prompt.target_skills,
        "hints": prompt.hints,
        "skill_cluster": cluster.model_dump() if cluster else None,
    }


@app.post("/api/session/submit")
def submit_response(req: SubmitResponseRequest):
    engine = get_engine(req.learner_id, target_language=req.target_language)
    if not engine.current_prompt:
        raise HTTPException(status_code=400, detail="No active prompt. Request /api/session/next-turn first.")

    analysis = engine.process_response(req.response_text, req.latency_ms)
    progress = engine.compute_progress()

    return {
        "analysis": {
            "semantic_correctness": round(analysis.semantic_correctness, 2),
            "grammar_accuracy": round(analysis.grammar_accuracy, 2),
            "naturalness": round(analysis.naturalness, 2),
            "pragmatic_appropriateness": round(analysis.pragmatic_appropriateness, 2),
            "detected_skills": analysis.detected_skills,
            "parsed_ir": analysis.parsed_ir,
            "latency_ms": req.latency_ms,
        },
        "progress": progress.model_dump(),
    }


@app.post("/api/transform")
def transform_ir(req: IRTransformRequest):
    """Bidirectional transformation between JA ↔ ES ↔ EN ↔ IR."""
    try:
        if req.source_language == "ja":
            ir = ja_adapter.parse(req.text_or_json)
        elif req.source_language == "en":
            ir = en_adapter.parse(req.text_or_json)
        elif req.source_language == "es":
            ir = es_adapter.parse(req.text_or_json)
        elif req.source_language == "ir":
            import json
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
    
    if req.target_language == "es":
        simulated_responses = [
            ("Si llueve mañana, no saldré.", 1300.0),
            ("Quiero comer ramen.", 1000.0),
            ("Un vaso de agua, por favor.", 750.0),
            ("He estado en Japón.", 1450.0),
            ("Creo que es muy delicioso.", 1100.0),
            ("Quiero vivir en Tokio.", 1200.0),
        ]
    else:
        simulated_responses = [
            ("明日雨が降ったら、東京に行きません。", 1350.0),
            ("ラーメンを食べたいです。", 1050.0),
            ("お水をください。", 800.0),
            ("日本に行ったことがあります。", 1500.0),
            ("美味しいと思います。", 1150.0),
            ("東京に住みたいです。", 1250.0),
        ]

    history = []
    for i in range(req.turns):
        resp, lat = simulated_responses[i % len(simulated_responses)]
        prompt = engine.start_next_turn()
        analysis = engine.process_response(resp, lat)
        prog = engine.compute_progress()
        history.append({
            "turn": engine.session_turn_count,
            "scenario": prompt.scenario_id,
            "target_skills": prompt.target_skills,
            "response": resp,
            "latency_ms": lat,
            "overall_mastery": prog.overall,
            "production": prog.dimensions.production,
            "retention": prog.dimensions.retention,
            "automaticity": prog.dimensions.automaticity,
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
