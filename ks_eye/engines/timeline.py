"""
ks-eye v2.0 — Timeline Builder
Extracts chronological events from research and builds a timeline.
"""

import json
import os
import time
from datetime import datetime

from ks_eye.engines.scraper import scrape_topic
from ks_eye.engines.analyzer import analyze_scraped_data
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.config import config
from ks_eye.ui import console, make_progress, show_section


TIMELINE_PROMPT = """You are a Timeline Builder. Extract ALL chronological events from this research.

TOPIC: {topic}

=== RESEARCH ===
{analysis}
=== END ===

Extract every dated event and arrange them chronologically.

For each event, provide:
- DATE: Year/month (be as specific as possible, use "approx." if uncertain)
- EVENT: What happened (2-3 sentences)
- SIGNIFICANCE: Why it matters (1 sentence)
- SOURCES: Which source(s) mention this

Format as a clean timeline with clear visual separators between eras/periods.
Include future projections if the research mentions them.
Group into logical periods if possible (e.g., "Early Period (2000-2010)", "Modern Era (2010-2020)")."""


def build_timeline(topic, depth=2, provider="sky"):
    """
    Scrape research on a topic and extract a chronological timeline.

    Returns:
        dict with timeline text, folder, metadata
    """
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║         📅 TIMELINE BUILDER                             ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    console.print(f"  Topic: {topic}")
    console.print()

    start = time.time()

    # Scrape
    show_section("SCRAPING RESEARCH")
    scrape_result = scrape_topic(topic, depth=depth, provider=provider)

    if scrape_result["scraped_count"] == 0:
        return {"status": "failed", "error": "No content scraped"}

    # Analyze
    show_section("ANALYZING")
    analysis = analyze_scraped_data(topic, scrape_result["sources"], provider=provider)

    if analysis.get("status") != "complete":
        return {"status": "failed", "error": "Analysis failed"}

    # Build timeline
    show_section("EXTRACTING TIMELINE")
    console.print(f"[dim]  🤖 AI is extracting chronological events...[/dim]")

    timeline_prompt = TIMELINE_PROMPT.format(
        topic=topic,
        analysis=analysis["analysis"][:10000],
    )

    timeline_text = run_tgpt(timeline_prompt, provider, timeout=240)

    if not timeline_text or len(timeline_text) < 100:
        return {"status": "failed", "error": "Timeline extraction failed"}

    elapsed = time.time() - start

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() else "_" for c in topic)[:50]
    folder = os.path.join(config.RESEARCH_DIR, f"timeline_{safe}_{ts}")
    os.makedirs(folder, exist_ok=True)

    out_file = os.path.join(folder, "timeline.txt")
    with open(out_file, "w") as f:
        f.write(f"TIMELINE: {topic}\n{'=' * 80}\n")
        f.write(f"Sources: {scrape_result['scraped_count']} | Time: {elapsed:.1f}s\n\n")
        f.write(timeline_text)

    # Also save full analysis
    with open(os.path.join(folder, "analysis.txt"), "w") as f:
        f.write(analysis["analysis"])

    meta = {
        "type": "timeline",
        "topic": topic,
        "sources": scrape_result["scraped_count"],
        "elapsed_seconds": round(elapsed, 1),
        "folder": folder,
        "output_file": out_file,
        "generated_at": datetime.now().isoformat(),
    }
    with open(os.path.join(folder, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    config.save_session(meta)

    console.print(f"\n[bold green]✓ Timeline saved → {out_file}[/bold green]")

    # Display preview
    from rich.panel import Panel
    console.print(Panel(
        timeline_text[:2000] + ("\n\n..." if len(timeline_text) > 2000 else ""),
        title=f"📅 Timeline: {topic}",
        border_style="green",
    ))

    return {
        "status": "complete",
        "folder": folder,
        "output_file": out_file,
        "timeline_text": timeline_text,
        "sources": scrape_result["scraped_count"],
    }
