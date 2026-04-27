"""
ks-eye v2.0 — Comparative Research Engine
Research two topics side-by-side with structured comparison.
"""

import json
import os
import time
from datetime import datetime

from ks_eye.engines.scraper import scrape_topic
from ks_eye.engines.prompt_rewriter import rewrite_for_search, rewrite_for_analysis
from ks_eye.engines.analyzer import analyze_scraped_data, validate_analysis
from ks_eye.engines.reporter import save_research_package
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.config import config
from ks_eye.ui import console, make_progress, show_section


COMPARE_PROMPT = """You are a Comparative Analyst. Two research topics have been analyzed independently.

TOPIC A: {topic_a}
=== ANALYSIS A ===
{analysis_a}
=== END A ===

TOPIC B: {topic_b}
=== ANALYSIS B ===
{analysis_b}
=== END B ===

Produce a comprehensive comparison (2000-3000 words):

1. OVERVIEW: What each topic is about (brief)
2. KEY SIMILARITIES: Where they overlap, share mechanisms, or have parallel dynamics
3. KEY DIFFERENCES: Where they diverge fundamentally
4. DATA COMPARISON: Side-by-side statistics, evidence, scale
5. CAUSAL FACTORS: What drives differences between them
6. IMPLICATIONS: What the comparison reveals that studying each alone would miss
7. SYNTHESIS: What we learn from comparing them
8. CONCLUSION: Bottom-line assessment

Use clear comparative language. Avoid just describing each separately — always compare."""


def comparative_research(topic_a, topic_b, output_type="report", depth=2, provider="sky"):
    """
    Research two topics independently, then compare.

    Returns:
        dict with comparison output, folder, metadata
    """
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║         ⚖️  COMPARATIVE RESEARCH ENGINE                 ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    console.print(f"  Topic A: {topic_a}")
    console.print(f"  Topic B: {topic_b}")
    console.print(f"  Provider: {provider}")
    console.print()

    start = time.time()

    # ── Research Topic A ──
    show_section("RESEARCHING TOPIC A")
    search_a = rewrite_for_search(topic_a)
    plan_a = rewrite_for_analysis(topic_a)
    scrape_a = scrape_topic(topic_a, depth=depth, provider=provider)
    analysis_a = analyze_scraped_data(topic_a, scrape_a["sources"], analysis_plan=plan_a, provider=provider)

    if analysis_a.get("status") != "complete":
        return {"status": "failed", "error": "Topic A analysis failed"}

    # ── Research Topic B ──
    show_section("RESEARCHING TOPIC B")
    search_b = rewrite_for_search(topic_b)
    plan_b = rewrite_for_analysis(topic_b)
    scrape_b = scrape_topic(topic_b, depth=depth, provider=provider)
    analysis_b = analyze_scraped_data(topic_b, scrape_b["sources"], analysis_plan=plan_b, provider=provider)

    if analysis_b.get("status") != "complete":
        return {"status": "failed", "error": "Topic B analysis failed"}

    # ── Compare ──
    show_section("COMPARING: A vs B")
    console.print(f"[dim]  🤖 AI is generating comparison...[/dim]")

    compare_prompt = COMPARE_PROMPT.format(
        topic_a=topic_a,
        topic_b=topic_b,
        analysis_a=analysis_a["analysis"][:8000],
        analysis_b=analysis_b["analysis"][:8000],
    )

    comparison_text = run_tgpt(compare_prompt, provider, timeout=300)

    if not comparison_text or len(comparison_text) < 200:
        return {"status": "failed", "error": "Comparison generation failed"}

    elapsed = time.time() - start
    console.print(f"[dim]  ✓ Comparison complete ({len(comparison_text)} chars)[/dim]")

    # ── Save ──
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_a = "".join(c if c.isalnum() else "_" for c in topic_a)[:25]
    safe_b = "".join(c if c.isalnum() else "_" for c in topic_b)[:25]
    folder = os.path.join(config.RESEARCH_DIR, f"compare_{safe_a}_vs_{safe_b}_{ts}")
    os.makedirs(folder, exist_ok=True)

    # Save comparison
    out_file = os.path.join(folder, f"comparison_{output_type}.txt")
    with open(out_file, "w") as f:
        f.write(f"{'=' * 80}\nCOMPARATIVE RESEARCH\n")
        f.write(f"Topic A: {topic_a}\nTopic B: {topic_b}\n")
        f.write(f"Sources A: {scrape_a['scraped_count']} | Sources B: {scrape_b['scraped_count']}\n")
        f.write(f"Time: {elapsed:.1f}s | Provider: {provider}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(comparison_text)

    # Save both analyses
    with open(os.path.join(folder, "analysis_a.txt"), "w") as f:
        f.write(analysis_a["analysis"])
    with open(os.path.join(folder, "analysis_b.txt"), "w") as f:
        f.write(analysis_b["analysis"])

    # Metadata
    meta = {
        "type": "comparative",
        "topic_a": topic_a,
        "topic_b": topic_b,
        "output_type": output_type,
        "sources_a": scrape_a["scraped_count"],
        "sources_b": scrape_b["scraped_count"],
        "elapsed_seconds": round(elapsed, 1),
        "folder": folder,
        "output_file": out_file,
        "generated_at": datetime.now().isoformat(),
    }
    with open(os.path.join(folder, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    config.save_session(meta)

    console.print(f"\n[bold green]✓ Comparison saved → {out_file}[/bold green]")
    return {
        "status": "complete",
        "folder": folder,
        "output_file": out_file,
        "comparison_text": comparison_text,
        "topic_a": topic_a,
        "topic_b": topic_b,
    }
