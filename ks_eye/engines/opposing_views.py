"""
ks-eye v2.0 — Opposing Views Engine
Deliberately researches BOTH sides of controversial topics equally.
"""

import json
import os
import time
from datetime import datetime

from ks_eye.engines.scraper import scrape_topic
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.config import config
from ks_eye.ui import console, make_progress, show_section


OPPOSING_VIEWS_PROMPT = """You are an impartial analyst presenting BOTH sides of a controversial topic.

TOPIC: {topic}

=== SIDE A RESEARCH ===
{side_a}
=== END A ===

=== SIDE B RESEARCH ===
{side_b}
=== END B ===

Produce a balanced analysis (2000-3000 words):

1. THE TOPIC: What's controversial and why
2. SIDE A: "The case for [position A]" — present their strongest arguments fairly
3. SIDE B: "The case for [position B]" — present their strongest arguments fairly
4. WHERE THEY AGREE: Common ground, shared facts, overlapping concerns
5. WHERE THEY DISAGREE: Core disagreements, what each side gets right/wrong
6. EVIDENCE ASSESSMENT: Which side has stronger evidence? Be honest.
7. WHAT'S MISSED: What both sides overlook
8. CONCLUSION: Measured assessment without taking sides

CRITICAL: Present each side's arguments as STRONGLY as possible (steelmanning, not strawmanning).
Do NOT declare a winner unless one side clearly lacks evidence."""


def opposing_views(topic, side_a_label="Side A", side_b_label="Side B",
                   depth=2, provider="sky"):
    """
    Research both sides of a controversial topic.

    Args:
        topic: The controversial topic
        side_a_label: Name for position A (e.g., "Proponents")
        side_b_label: Name for position B (e.g., "Critics")
        depth: Scrape depth
        provider: AI provider

    Returns:
        dict with balanced analysis, folder, metadata
    """
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║         ⚖️  OPPOSING VIEWS ENGINE                       ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    console.print(f"  Topic: {topic}")
    console.print(f"  {side_a_label} vs {side_b_label}")
    console.print()

    start = time.time()

    # ── Scrape Side A ──
    query_a = f"evidence for arguments supporting {topic} {side_a_label}"
    console.print(f"[dim]  Scraping: {side_a_label} perspective...[/dim]")
    scrape_a = scrape_topic(query_a, depth=depth, provider=provider)

    # ── Scrape Side B ──
    query_b = f"evidence for arguments against {topic} {side_b_label} criticism"
    console.print(f"[dim]  Scraping: {side_b_label} perspective...[/dim]")
    scrape_b = scrape_topic(query_b, depth=depth, provider=provider)

    # ── Analyze Both Sides ──
    show_section("ANALYZING BOTH SIDES")

    side_a_content = "\n\n".join(
        f"[{s.get('title', '?')}] {s.get('scraped_content') or s.get('snippet', '')}"
        for s in scrape_a.get("sources", []) if s.get("scraped_content") or s.get("snippet")
    )[:5000]

    side_b_content = "\n\n".join(
        f"[{s.get('title', '?')}] {s.get('scraped_content') or s.get('snippet', '')}"
        for s in scrape_b.get("sources", []) if s.get("scraped_content") or s.get("snippet")
    )[:5000]

    # Generate balanced analysis
    console.print(f"[dim]  🤖 AI is generating balanced analysis...[/dim]")

    prompt = OPPOSING_VIEWS_PROMPT.format(
        topic=topic,
        side_a=side_a_content or f"Arguments for {side_a_label} on {topic}",
        side_b=side_b_content or f"Arguments for {side_b_label} on {topic}",
    )

    analysis_text = run_tgpt(prompt, provider, timeout=300)

    if not analysis_text or len(analysis_text) < 200:
        return {"status": "failed", "error": "Analysis generation failed"}

    elapsed = time.time() - start

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() else "_" for c in topic)[:50]
    folder = os.path.join(config.RESEARCH_DIR, f"opposing_{safe}_{ts}")
    os.makedirs(folder, exist_ok=True)

    out_file = os.path.join(folder, "opposing_views.txt")
    with open(out_file, "w") as f:
        f.write(f"OPPOSING VIEWS: {topic}\n{'=' * 80}\n")
        f.write(f"{side_a_label} vs {side_b_label}\n")
        f.write(f"Sources A: {scrape_a.get('scraped_count', 0)} | ")
        f.write(f"Sources B: {scrape_b.get('scraped_count', 0)}\n")
        f.write(f"Time: {elapsed:.1f}s | Provider: {provider}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(analysis_text)

    meta = {
        "type": "opposing_views",
        "topic": topic,
        "side_a_label": side_a_label,
        "side_b_label": side_b_label,
        "sources_a": scrape_a.get("scraped_count", 0),
        "sources_b": scrape_b.get("scraped_count", 0),
        "elapsed_seconds": round(elapsed, 1),
        "folder": folder,
        "output_file": out_file,
        "generated_at": datetime.now().isoformat(),
    }
    with open(os.path.join(folder, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    config.save_session(meta)

    console.print(f"\n[bold green]✓ Opposing views saved → {out_file}[/bold green]")

    from rich.panel import Panel
    console.print(Panel(
        analysis_text[:2000] + ("\n\n..." if len(analysis_text) > 2000 else ""),
        title=f"⚖️ {topic}: {side_a_label} vs {side_b_label}",
        border_style="green",
    ))

    return {
        "status": "complete",
        "folder": folder,
        "output_file": out_file,
        "analysis_text": analysis_text,
    }
