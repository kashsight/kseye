"""
ks-eye v2.0 — Batch Research Engine
Queue multiple topics → research all of them sequentially.
"""

import json
import os
import time
from datetime import datetime

from ks_eye.engines.scraper import scrape_topic
from ks_eye.engines.analyzer import analyze_scraped_data
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.config import config
from ks_eye.ui import console, make_progress, show_section, show_success, show_error


def batch_research(topics, output_type="report", depth=2, provider="sky"):
    """
    Research multiple topics in a batch.

    Args:
        topics: List of topic strings
        output_type: Output format
        depth: Scrape depth
        provider: AI provider

    Returns:
        dict with all results, summary, folder
    """
    console.print()
    console.print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║         📦 BATCH RESEARCH ENGINE                        ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    console.print(f"  Topics: {len(topics)}")
    console.print(f"  Output: {output_type}")
    console.print(f"  Depth: {depth}")
    console.print()

    # Show queue
    for i, t in enumerate(topics, 1):
        console.print(f"  {i}. {t[:80]}{'...' if len(t) > 80 else ''}")
    console.print()

    start = time.time()
    results = []
    errors = []

    for i, topic in enumerate(topics, 1):
        show_section(f"TOPIC {i}/{len(topics)}: {topic[:60]}")

        try:
            # Scrape
            scrape_result = scrape_topic(topic, depth=depth, provider=provider)

            if scrape_result["scraped_count"] == 0:
                show_error(f"No content for: {topic}")
                errors.append({"topic": topic, "error": "No content scraped"})
                continue

            # Analyze
            analysis = analyze_scraped_data(topic, scrape_result["sources"], provider=provider)

            if analysis.get("status") != "complete":
                show_error(f"Analysis failed for: {topic}")
                errors.append({"topic": topic, "error": "Analysis failed"})
                continue

            # Generate output
            console.print(f"[dim]  🤖 Generating {output_type}...[/dim]")
            output_prompt = (
                f"Write a comprehensive {output_type} about: {topic}\n\n"
                f"Based on this analysis:\n\n{analysis['analysis'][:10000]}\n\n"
                f"Include: key findings, evidence, different perspectives, conclusions."
            )
            output_text = run_tgpt(output_prompt, provider, timeout=240)

            if not output_text:
                show_error(f"Output generation failed for: {topic}")
                errors.append({"topic": topic, "error": "Output generation failed"})
                continue

            # Save individual result
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe = "".join(c if c.isalnum() else "_" for c in topic)[:50]
            folder = os.path.join(config.RESEARCH_DIR, f"batch_{safe}_{ts}")
            os.makedirs(folder, exist_ok=True)

            out_file = os.path.join(folder, f"{output_type}.txt")
            with open(out_file, "w") as f:
                f.write(f"{'=' * 80}\n{output_type.upper()}: {topic}\n")
                f.write(f"Sources: {scrape_result['scraped_count']} | ")
                f.write(f"Analysis: {len(analysis['analysis'])} chars\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(output_text)

            meta = {
                "topic": topic,
                "output_type": output_type,
                "sources": scrape_result["scraped_count"],
                "folder": folder,
                "output_file": out_file,
                "generated_at": datetime.now().isoformat(),
            }
            with open(os.path.join(folder, "metadata.json"), "w") as f:
                json.dump(meta, f, indent=2)

            results.append({
                "topic": topic,
                "folder": folder,
                "output_file": out_file,
                "sources": scrape_result["scraped_count"],
                "analysis_chars": len(analysis["analysis"]),
                "output_chars": len(output_text),
            })

            show_success(f"Done → {out_file}")

        except Exception as e:
            show_error(f"Error on '{topic}': {e}")
            errors.append({"topic": topic, "error": str(e)})

    elapsed = time.time() - start

    # Batch summary
    show_section("BATCH COMPLETE")
    console.print(f"  Successful: {len(results)}/{len(topics)}")
    console.print(f"  Failed: {len(errors)}")
    console.print(f"  Total time: {elapsed:.1f}s")
    console.print(f"  Average per topic: {elapsed/len(topics):.1f}s")

    # Save batch metadata
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_folder = os.path.join(config.RESEARCH_DIR, f"batch_run_{ts}")
    os.makedirs(batch_folder, exist_ok=True)

    batch_meta = {
        "type": "batch",
        "topics": [r["topic"] for r in results],
        "successful": len(results),
        "failed": len(errors),
        "errors": errors,
        "total_time_seconds": round(elapsed, 1),
        "results": [r for r in results],
        "generated_at": datetime.now().isoformat(),
    }
    with open(os.path.join(batch_folder, "batch_summary.json"), "w") as f:
        json.dump(batch_meta, f, indent=2)

    config.save_session(batch_meta)

    return {
        "status": "complete",
        "successful": len(results),
        "failed": len(errors),
        "errors": errors,
        "total_time": round(elapsed, 1),
        "results": results,
        "batch_folder": batch_folder,
    }
