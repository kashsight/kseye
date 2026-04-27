"""
ks-eye v2.0 — Multi-Agent Research Engine
45 agents across 6 departments, hierarchical pipeline.
Rewritten from scratch with clean architecture.
"""

import json
import os
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.engines.citation_manager import CitationManager
from ks_eye.engines.export_formats import export_to_markdown
from ks_eye.engines.export_formatter import generate_html_report
from ks_eye.config import config
from ks_eye.ui import console, make_progress


# ═══════════════════════════════════════════════════════════
#  DEPARTMENT PROMPTS
# ═══════════════════════════════════════════════════════════

COLLECTORS = {
    "fact_finder": "Research: {topic}\n\nFind 7 key facts. For each: the fact, why it matters, confidence level (High/Medium/Low). Be specific with numbers.",
    "context_provider": "Research: {topic}\n\nProvide background context: history, evolution, current state. 500-800 words.",
    "stakeholder_mapper": "Research: {topic}\n\nIdentify all stakeholders. For each: who, how affected, influence level, position.",
    "trend_spotter": "Research: {topic}\n\nIdentify 5-7 trends. For each: direction, speed, evidence, impact.",
    "counterargument_scout": "Research: {topic}\n\nFind strongest arguments AGAINST the mainstream view. Present them fairly.",
    "data_point_miner": "Research: {topic}\n\nExtract numbers, statistics, percentages. Format: 'Statistic: [number] — [context]'. At least 10.",
    "case_study_hunter": "Research: {topic}\n\nFind 3-5 real-world examples. For each: what happened, who, outcome, lessons.",
    "expert_opinion_tracker": "Research: {topic}\n\nWhat do recognized experts say? Summarize positions. Where is consensus? Where disagreement?",
    "global_perspective_agent": "Research: {topic}\n\nHow does this look from different countries/regions? Cover 3-4 perspectives.",
    "future_scanner": "Research: {topic}\n\nLikely developments in 1, 5, 10 years. Scenarios: best, worst, most likely. Wildcards?",
}

VALIDATORS = {
    "credibility_checker": "Review credibility of this research.\n\n{research_text}\n\nFlag unsupported claims, weak reasoning. Rate 1-10.",
    "bias_detector": "Review for bias.\n\n{research_text}\n\nCheck: selection bias, confirmation bias, framing bias. What perspectives are missing?",
    "logic_checker": "Check logical consistency.\n\n{research_text}\n\nFallacies, non sequiturs, false dichotomies. Are causal claims justified?",
    "recency_validator": "Check timeliness.\n\n{research_text}\n\nIs this current? Flag outdated claims.",
    "source_quality_checker": "Evaluate source reliability.\n\n{research_text}\n\nRate quality: Peer-reviewed / Expert opinion / Anecdotal / Unknown.",
    "sample_size_checker": "Check statistical claims.\n\n{research_text}\n\nAre sample sizes adequate? Flag small-n, cherry-picked data.",
    "correlation_checker": "Check causal claims.\n\n{research_text}\n\nDoes correlation imply causation? Flag unjustified causality.",
    "completeness_checker": "What's missing?\n\n{research_text}\n\nGaps, blind spots, unaddressed questions.",
    "consistency_checker": "Check contradictions.\n\n{research_text}\n\nDo different parts contradict each other? List inconsistencies.",
    "relevance_filter": "Assess relevance to topic: {topic}\n\n{research_text}\n\nRank: Essential / Useful / Tangential / Irrelevant.",
    "strength_rater": "Rate evidence strength.\n\n{research_text}\n\nFor each major claim: Strong/Moderate/Weak. Overall 1-10.",
    "alternative_explainer": "Alternative explanations.\n\n{research_text}\n\nWhat other interpretations could account for these findings? 2-3 alternatives.",
    "extreme_case_tester": "Stress-test with edge cases.\n\n{research_text}\n\nDo claims hold in extreme cases? Where do they break?",
    "peer_review_sim": "Simulate peer review.\n\n{research_text}\n\nWould this pass? Major/minor issues. Reviewer-style critique.",
    "fact_ground_truth": "Topic: {topic}\n\nWhat are indisputable facts?\n\n{research_text}\n\nSeparate facts from speculation.",
}

ANALYSTS = {
    "synthesizer": "Synthesize into unified analysis.\n\n=== RESEARCH ===\n{research_text}\n\n=== VALIDATION ===\n{validation_text}\n\nBig picture, key themes, surprises. 800-1200 words.",
    "pattern_analyst": "Find patterns.\n\n=== RESEARCH ===\n{research_text}\n\n=== VALIDATION ===\n{validation_text}\n\nWhat clusters together? Underlying structure?",
    "insight_generator": "Generate non-obvious insights.\n\n=== RESEARCH ===\n{research_text}\n\n=== VALIDATION ===\n{validation_text}\n\n5-7 insights that would surprise an informed reader.",
    "implication_mapper": "Map implications.\n\n=== RESEARCH ===\n{research_text}\n\n=== VALIDATION ===\n{validation_text}\n\nShort-term, medium-term, long-term. What should stakeholders do differently?",
    "gap_analyst": "Identify knowledge gaps.\n\n=== RESEARCH ===\n{research_text}\n\n=== VALIDATION ===\n{validation_text}\n\nWhat don't we know? Where is more research needed?",
}

SUMMARIZERS = {
    "executive_summarizer": "Executive summary of:\n\n{analysis_text}\n\n300-500 words. Core message, key findings, bottom line.",
    "key_points_extractor": "Extract 10 key points:\n\n{analysis_text}\n\nOne clear sentence each.",
    "takeaway_compiler": "5-7 actionable takeaways:\n\n{analysis_text}\n\nEach: what to do + why.",
    "narrative_weaver": "Weave into a narrative:\n\n{analysis_text}\n\nStory arc: setup → tension → resolution. 600-800 words.",
    "context_connector": "Connect to broader context:\n\n{analysis_text}\n\nHow does this connect to bigger trends, history, related fields? 400-600 words.",
}

WRITERS = {
    "summary": {
        "system": "Write a concise summary.",
        "prompt": "Topic: {topic}\n\nWrite an executive summary (500-800 words).\n\n=== ANALYSIS ===\n{analysis_text}\n\nMain finding, key evidence, bottom line.",
    },
    "report": {
        "system": "Write a comprehensive research report.",
        "prompt": "Topic: {topic}\n\nWrite a full report (2000-3000 words): Executive Summary, Background, Key Findings, Data/Statistics, Different Perspectives, Limitations, Conclusions.\n\n=== ANALYSIS ===\n{analysis_text}\n\nProfessional, evidence-based.",
    },
    "blog": {
        "system": "Write an engaging blog post.",
        "prompt": "Topic: {topic}\n\nWrite a blog post (1500-2000 words): compelling headline, hook, organized sections, examples, conversational but authoritative.\n\n=== ANALYSIS ===\n{analysis_text}\n\nMake it shareable.",
    },
    "guide": {
        "system": "Write a step-by-step guide.",
        "prompt": "Topic: {topic}\n\nWrite a step-by-step guide (1500-2000 words): overview, 8-12 numbered steps, mistakes to avoid, tips.\n\n=== ANALYSIS ===\n{analysis_text}\n\nClear and actionable.",
    },
    "proposal": {
        "system": "Write a research proposal.",
        "prompt": "Topic: {topic}\n\nWrite a research proposal (1500-2000 words): Introduction, Problem Statement, Research Questions, Methodology, Expected Contributions, Timeline.\n\n=== ANALYSIS ===\n{analysis_text}\n\nAcademic tone.",
    },
}

EDITORS = {
    "clarity_editor": "Rewrite for clarity:\n\n{draft_text}\n\nEliminate jargon, simplify, clarify ambiguities. Return the FULL edited text.",
    "flow_editor": "Improve flow:\n\n{draft_text}\n\nBetter transitions, logical progression. Return the FULL edited text.",
    "tone_editor": "Adjust tone:\n\n{draft_text}\n\nMake it appropriate for the audience. Return the FULL edited text.",
    "brevity_editor": "Cut fluff:\n\n{draft_text}\n\nRemove repetition and filler. 15-20% shorter. Return the FULL edited text.",
    "impact_editor": "Strengthen impact:\n\n{draft_text}\n\nMake key passages memorable. Return the FULL edited text.",
}


# ═══════════════════════════════════════════════════════════
#  AGENT EXECUTION
# ═══════════════════════════════════════════════════════════

class AgentResult:
    def __init__(self, name, output, status="success", error=None):
        self.name = name
        self.output = output if output and len(output.strip()) > 0 else ""
        self.status = status
        self.error = error

    @property
    def ok(self):
        return self.status == "success" and len(self.output) > 0


def run_agent(name, prompt, provider, timeout=120):
    """Run a single agent with retry."""
    for attempt in range(2):
        try:
            output = run_tgpt(prompt, provider, timeout=timeout)
            if output and len(output.strip()) > 20:
                return AgentResult(name, output.strip())
        except Exception as e:
            if attempt == 0:
                continue
            return AgentResult(name, "", status="error", error=str(e))
    return AgentResult(name, "", status="error", error="Empty response")


def run_department_parallel(name, prompts, context, provider, max_workers=8):
    """Run agents in parallel with context substitution."""
    console.print(f"[bold cyan]  └─ {name} ({len(prompts)} agents)[/bold cyan]")

    results = []

    def _run(agent_name, template):
        prompt = template.format(**context) if context else template
        return run_agent(agent_name, prompt, provider)

    with ThreadPoolExecutor(max_workers=min(max_workers, len(prompts))) as ex:
        futures = {ex.submit(_run, n, t): n for n, t in prompts.items()}
        for f in as_completed(futures):
            r = f.result()
            results.append(r)
            console.print(f"      {'✓' if r.ok else '✗'} {r.name}")

    return results


def _combine(results):
    """Combine successful agent outputs."""
    parts = [r.output for r in results if r.ok]
    return "\n\n" + "=" * 70 + "\n\n".join(parts)


def _success_count(results):
    return sum(1 for r in results if r.ok)


# ═══════════════════════════════════════════════════════════
#  MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════

def multi_agent_research(topic, output_type="report", provider="sky"):
    """
    Full 45-agent research pipeline.

    Returns dict with folder, output_file, metadata.
    """
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║      🏢 MULTI-AGENT RESEARCH — 45 AGENTS               ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    console.print(f"  Topic: {topic}")
    console.print(f"  Output: {output_type}")
    console.print(f"  Provider: {provider}")
    console.print()

    start = time.time()
    all_dept = {}

    # ── DEPT 1: COLLECTORS ──
    console.print("[bold green]━━━ DEPT 1: DATA COLLECTION (10) ━━━[/bold green]")
    collector_results = run_department_parallel("Collectors", COLLECTORS, {"topic": topic}, provider)
    all_dept["collectors"] = collector_results
    research_text = _combine(collector_results)
    console.print(f"[dim]  ✓ {_success_count(collector_results)}/10[/dim]\n")

    # ── DEPT 2: VALIDATORS ──
    console.print("[bold green]━━━ DEPT 2: VALIDATION (15) ━━━[/bold green]")
    validator_results = run_department_parallel(
        "Validators", VALIDATORS,
        {"topic": topic, "research_text": research_text[:12000]},
        provider
    )
    all_dept["validators"] = validator_results
    validation_text = _combine(validator_results)
    console.print(f"[dim]  ✓ {_success_count(validator_results)}/15[/dim]\n")

    # ── DEPT 3: ANALYSTS ──
    console.print("[bold green]━━━ DEPT 3: ANALYSIS (5) ━━━[/bold green]")
    analyst_results = run_department_parallel(
        "Analysts", ANALYSTS,
        {"research_text": research_text[:10000], "validation_text": validation_text[:8000]},
        provider
    )
    all_dept["analysts"] = analyst_results
    analysis_text = _combine(analyst_results)
    console.print(f"[dim]  ✓ {_success_count(analyst_results)}/5[/dim]\n")

    # ── DEPT 4: SUMMARIZERS ──
    console.print("[bold green]━━━ DEPT 4: SUMMARIZATION (5) ━━━[/bold green]")
    summarizer_results = run_department_parallel(
        "Summarizers", SUMMARIZERS,
        {"analysis_text": analysis_text[:10000]},
        provider
    )
    all_dept["summarizers"] = summarizer_results
    summary_text = _combine(summarizer_results)
    console.print(f"[dim]  ✓ {_success_count(summarizer_results)}/5[/dim]\n")

    # ── DEPT 5: WRITER ──
    console.print(f"[bold green]━━━ DEPT 5: WRITING ({output_type}) ━━━[/bold green]")
    writer_config = WRITERS.get(output_type, WRITERS["report"])
    writer_prompt = writer_config["prompt"].format(topic=topic, analysis_text=analysis_text[:10000])
    writer_result = run_agent(f"{output_type}_writer", writer_prompt, provider, timeout=300)
    draft_text = writer_result.output if writer_result.ok else analysis_text
    console.print(f"      {'✓' if writer_result.ok else '✗'} {output_type}_writer\n")

    # ── DEPT 6: EDITORS ──
    console.print("[bold green]━━━ DEPT 6: EDITING (5) ━━━[/bold green]")
    editor_results = run_department_parallel(
        "Editors", EDITORS,
        {"draft_text": draft_text[:12000]},
        provider
    )
    all_dept["editors"] = editor_results
    # Use the best editor output (clarity_editor as primary)
    final_text = ""
    for r in editor_results:
        if r.name == "clarity_editor" and r.ok:
            final_text = r.output
            break
    if not final_text:
        final_text = draft_text
    console.print(f"[dim]  ✓ {_success_count(editor_results)}/5[/dim]\n")

    # ── STATS ──
    elapsed = time.time() - start
    total_ok = sum(_success_count(r) for r in all_dept.values())
    total_ok += 1 if writer_result.ok else 0
    total_agents = sum(len(r) for r in all_dept.values()) + 1

    # ── SAVE ──
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() else "_" for c in topic)[:50]
    folder = os.path.join(config.RESEARCH_DIR, f"multi_{safe}_{ts}")
    os.makedirs(folder, exist_ok=True)

    # Primary output
    out_file = os.path.join(folder, f"final_{output_type}.txt")
    with open(out_file, "w") as f:
        f.write(f"{'=' * 80}\nMULTI-AGENT RESEARCH\nTopic: {topic}\nType: {output_type}\n")
        f.write(f"Agents: {total_ok}/{total_agents}  |  Time: {elapsed:.1f}s  |  Provider: {provider}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(final_text)
        f.write(f"\n\n{'=' * 80}\nALL DEPARTMENT OUTPUTS\n{'=' * 80}\n")
        for dept, results in all_dept.items():
            f.write(f"\n\n{'#' * 60}\n# {dept.upper()}\n{'#' * 60}\n")
            for r in results:
                f.write(f"\n--- {r.name} ({r.status}) ---\n")
                f.write(r.output if r.output else "[empty]\n")

    # Metadata
    meta = {
        "topic": topic,
        "output_type": output_type,
        "provider": provider,
        "agents_successful": total_ok,
        "agents_total": total_agents,
        "elapsed_seconds": round(elapsed, 1),
        "folder": folder,
        "output_file": out_file,
        "generated_at": datetime.now().isoformat(),
        "departments": {d: _success_count(r) for d, r in all_dept.items()},
    }
    meta_file = os.path.join(folder, "metadata.json")
    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=2)

    config.save_session(meta)

    # Summary display
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║           ✅ MULTI-AGENT RESEARCH COMPLETE              ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    console.print(f"  Agents: {total_ok}/{total_agents}")
    console.print(f"  Time: {elapsed:.1f}s")
    console.print(f"  Output: {out_file}")
    console.print(f"  Folder: {folder}")
    console.print()

    if final_text:
        from rich.panel import Panel
        console.print(Panel(
            final_text[:1500] + ("\n\n... [see full output in file]" if len(final_text) > 1500 else ""),
            title=f"📄 {output_type.title()} Preview",
            border_style="green",
        ))

    return {
        "status": "complete",
        "folder": folder,
        "output_file": out_file,
        "metadata_file": meta_file,
        "total_agents": total_ok,
        "elapsed_seconds": round(elapsed, 1),
        "output_type": output_type,
        "topic": topic,
    }
