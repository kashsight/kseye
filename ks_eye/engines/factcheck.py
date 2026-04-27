"""
ks-eye v2.0 — Fact-Check Engine
Takes claims, articles, or statements and verifies them against real sources.
"""

import json
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ks_eye.engines.scraper import scrape_topic
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.config import config
from ks_eye.ui import console, make_progress, show_section


FACT_CHECK_PROMPT = """You are a rigorous Fact-Checker. You will evaluate claims against evidence.

CLAIMS TO CHECK:
{claims}

=== EVIDENCE FROM REAL SOURCES ===
{evidence}
=== END EVIDENCE ===

For EACH claim, provide:

1. VERDICT: True / Mostly True / Mixed / Mostly False / False / Unverifiable
2. EVIDENCE FOR: What supports this claim (quote sources)
3. EVIDENCE AGAINST: What contradicts this claim (quote sources)
4. NUANCE: Important context or caveats
5. CONFIDENCE: How certain are you (High / Medium / Low)
6. EXPLANATION: 2-3 sentences explaining your reasoning

Be strict. A claim is only "True" if the evidence clearly supports it.
If evidence is inconclusive, say so. Don't hedge — give clear verdicts."""


def fact_check(claims_text, depth=2, provider="sky"):
    """
    Fact-check claims against real scraped sources.

    Args:
        claims_text: Claims to check (one per line or numbered)
        depth: Scrape depth
        provider: AI provider

    Returns:
        dict with verdicts, evidence, output file
    """
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║         🔍 FACT-CHECK ENGINE                            ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")

    # Parse claims
    claims_list = [c.strip() for c in claims_text.strip().split("\n") if c.strip()]
    if not claims_list:
        return {"status": "failed", "error": "No claims provided"}

    console.print(f"  Claims to check: {len(claims_list)}")
    for i, claim in enumerate(claims_list, 1):
        console.print(f"    {i}. {claim[:80]}{'...' if len(claim) > 80 else ''}")

    # Extract topic from claims for scraping
    topic_prompt = (
        f"Given these claims, what is the main topic? Answer in 5-8 words.\n\n"
        f"{' | '.join(claims_list[:5])}"
    )
    topic = run_tgpt(topic_prompt, "sky", timeout=15)
    if not topic or len(topic) < 5:
        topic = claims_list[0][:100]
    topic = topic.strip()
    console.print(f"\n  Derived topic: {topic}")

    # Scrape evidence
    show_section("SCRAPING EVIDENCE")
    scrape_result = scrape_topic(topic, depth=depth, provider=provider)

    if scrape_result["scraped_count"] == 0:
        return {"status": "failed", "error": "No evidence could be scraped"}

    # Build evidence text
    evidence_parts = []
    for i, source in enumerate(scrape_result["sources"], 1):
        content = source.get("scraped_content") or source.get("snippet") or ""
        if content:
            evidence_parts.append(f"SOURCE #{i}: {source.get('title', 'Untitled')}")
            evidence_parts.append(f"URL: {source.get('url', 'unknown')}")
            evidence_parts.append(content[:3000])
            evidence_parts.append("")

    evidence_text = "\n".join(evidence_parts)

    # Fact-check
    show_section("FACT-CHECKING")
    console.print(f"[dim]  🤖 AI is checking {len(claims_list)} claims against {scrape_result['scraped_count']} sources...[/dim]")

    fc_prompt = FACT_CHECK_PROMPT.format(
        claims="\n".join(f"{i}. {c}" for i, c in enumerate(claims_list, 1)),
        evidence=evidence_text[:15000],
    )

    verdicts_text = run_tgpt(fc_prompt, provider, timeout=300)

    if not verdicts_text:
        return {"status": "failed", "error": "Fact-check returned empty"}

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(config.RESEARCH_DIR, f"factcheck_{ts}")
    os.makedirs(folder, exist_ok=True)

    out_file = os.path.join(folder, "fact_check.txt")
    with open(out_file, "w") as f:
        f.write(f"FACT-CHECK REPORT\n{'=' * 80}\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Claims checked: {len(claims_list)}\n")
        f.write(f"Sources consulted: {scrape_result['scraped_count']}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write("CLAIMS:\n")
        for i, c in enumerate(claims_list, 1):
            f.write(f"  {i}. {c}\n")
        f.write(f"\n{'=' * 80}\n\nVERDICTS:\n\n")
        f.write(verdicts_text)

    meta = {
        "type": "fact_check",
        "topic": topic,
        "claims_count": len(claims_list),
        "sources_consulted": scrape_result["scraped_count"],
        "folder": folder,
        "output_file": out_file,
        "generated_at": datetime.now().isoformat(),
    }
    with open(os.path.join(folder, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    config.save_session(meta)

    console.print(f"\n[bold green]✓ Fact-check saved → {out_file}[/bold green]")

    # Show verdicts summary
    console.print(f"\n[bold]Verdicts Summary:[/bold]")
    console.print(verdicts_text[:1500])

    return {
        "status": "complete",
        "folder": folder,
        "output_file": out_file,
        "verdicts": verdicts_text,
        "claims_checked": len(claims_list),
        "sources_consulted": scrape_result["scraped_count"],
    }
