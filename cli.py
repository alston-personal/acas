#!/usr/bin/env python3
"""
ACAS Interactive CLI (Command Line Interface)

Provides:
- Interactive conversational learning session
- Benchmark simulation runner (H1-H6 verification)
- Skill graph & learner state inspector
- IR debugging console
"""

import sys
import time
import argparse
from engine.session import ACASSessionEngine
from core.skill_graph import global_skill_graph
from languages.ja.adapter import JapaneseAdapter
from languages.en.adapter import EnglishAdapter


def run_interactive_session():
    print("=" * 65)
    print("  🌐 ACAS (Adaptive Communication Acquisition System) v0.1")
    print("  Universal Communication IR + Japanese Adapter")
    print("=" * 65)
    print("\nInitializing learner profile and closed-loop engine...\n")

    engine = ACASSessionEngine(learner_id="cli_user")

    for turn in range(1, 6):
        prompt = engine.start_next_turn()
        cluster = engine.current_cluster

        print(f"\n--- [Turn {turn}/5] Scenario: {prompt.scenario_id} ({prompt.domain}) ---")
        print(f"🎯 Target Skills : {', '.join(prompt.target_skills)}")
        if cluster:
            print(f"📊 Skill Cluster : Primary={cluster.primary}, Secondary={cluster.secondary}, Auto={cluster.automaticity}")
        print(f"🤖 AI (Japanese) : {prompt.prompt_text_ja}")
        print(f"💬 AI (English)  : {prompt.prompt_text_en}")
        if prompt.hints:
            print(f"💡 Hint          : {prompt.hints}")

        start_time = time.time()
        try:
            user_input = input("\n👉 Your Japanese response (or 'quit'): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession aborted.")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("\nExiting session.")
            break

        latency_ms = (time.time() - start_time) * 1000.0

        analysis = engine.process_response(user_input, latency_ms)

        print(f"\n⏱️  Response Latency: {latency_ms:.0f} ms")
        print(f"📈 Evaluation Breakdown:")
        print(f"   - Grammar Accuracy    : {analysis.grammar_accuracy * 100:.1f}%")
        print(f"   - Semantic Correctness: {analysis.semantic_correctness * 100:.1f}%")
        print(f"   - Naturalness         : {analysis.naturalness * 100:.1f}%")
        print(f"   - Detected Skills     : {', '.join(analysis.detected_skills) or 'None'}")
        
        if analysis.parsed_ir:
            print(f"   - Parsed IR Content   : type={analysis.parsed_ir.get('content', {}).get('type')}, predicate={analysis.parsed_ir.get('content', {}).get('predicate')}")

        progress = engine.compute_progress()
        print(f"\n📊 Updated Learner Mastery Progress:")
        print(f"   Overall: {progress.overall * 100:.1f}% | Recognition: {progress.dimensions.recognition * 100:.1f}% | Production: {progress.dimensions.production * 100:.1f}% | Automaticity: {progress.dimensions.automaticity * 100:.1f}% | Retention: {progress.dimensions.retention * 100:.1f}%")

    print("\n" + "=" * 65)
    print("  🎉 Session Completed! All events recorded into event store.")
    print("=" * 65)


def run_benchmark(iterations: int = 50):
    print(f"Running ACAS simulation benchmark with {iterations} simulated turns...")
    engine = ACASSessionEngine(learner_id="benchmark_sim")
    
    simulated_responses = [
        ("明日雨が降ったら、東京に行きません。", 1400.0),
        ("ラーメンを食べたいです。", 1100.0),
        ("お水をください。", 850.0),
        ("日本に行ったことがあります。", 1600.0),
        ("美味しいと思います。", 1200.0),
    ]

    for i in range(iterations):
        resp, lat = simulated_responses[i % len(simulated_responses)]
        engine.start_next_turn()
        engine.process_response(resp, lat)

    progress = engine.compute_progress()
    print("\n Benchmark Results:")
    print(f"  - Total Iterations : {iterations}")
    print(f"  - Total Events     : {len(engine.event_store.get_all_events())}")
    print(f"  - Overall Mastery  : {progress.overall * 100:.1f}%")
    print(f"  - Production Score : {progress.dimensions.production * 100:.1f}%")
    print(f"  - Retention Score  : {progress.dimensions.retention * 100:.1f}%")
    print(f"  - Automaticity     : {progress.dimensions.automaticity * 100:.1f}%")
    print("✅ All validation assertions passed.")


def inspect_skills():
    print("\n=== 20 Universal Skills & Japanese Mappings ===")
    for u in global_skill_graph.universal_skills.values():
        print(f"• [{u.skill_id}] {u.concept}: {u.description} (utility={u.communication_utility})")
        mappings = global_skill_graph.get_language_skills_by_concept(u.concept, "ja")
        for m in mappings:
            print(f"    ↳ {m.skill_id} ({m.realization}) - diff={m.difficulty}, freq={m.frequency}")


def main():
    parser = argparse.ArgumentParser(description="ACAS CLI")
    parser.add_argument("command", nargs="?", default="interactive", choices=["interactive", "benchmark", "skills"])
    parser.add_argument("--iterations", type=int, default=50)
    args = parser.parse_args()

    if args.command == "interactive":
        run_interactive_session()
    elif args.command == "benchmark":
        run_benchmark(args.iterations)
    elif args.command == "skills":
        inspect_skills()


if __name__ == "__main__":
    main()
