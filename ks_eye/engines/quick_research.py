"""
ks-eye Quick Online Research — AI-Powered Full Scraping Mode
Uses AI to scrape, analyze, and summarize in one shot.
"""

import json
from datetime import datetime

from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.engines.scholar_search import comprehensive_search
from ks_eye.ui import console


def quick_online_research(query, max_sources=30, provider="sky"):
    """
    Fully AI-powered research: scrapes web + academic sources,
    AI analyzes everything and produces a research brief.

    Args:
        query: Research query
        max_sources: Maximum sources to gather
        provider: AI provider to use

    Returns:
        Research brief dict with findings, sources, summary
    """
    results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "mode": "quick_online",
    }

    # Step 1: Scrape sources
    console.print("[cyan]🔍 Scraping online sources...[/cyan]")
    sources = comprehensive_search(query, max_sources=max_sources)
    results["sources"] = sources
    results["source_count"] = len(sources)
    console.print(f"[green]✓ Found {len(sources)} sources[/green]")

    if not sources:
        results["status"] = "error"
        results["message"] = "No sources found"
        return results

    # Step 2: AI analyzes all sources
    console.print("[cyan]🤖 AI analyzing sources...[/cyan]")
    sources_summary = "\n".join([
        f"[{i+1}] {s.get('title', '')}\n    Source: {s.get('source', '')}\n    Summary: {s.get('snippet', '')}"
        for i, s in enumerate(sources[:20])
    ])

    ai_prompt = (
        "You are a research analyst. I will give you a list of academic and web sources "
        "about a topic. Your job is to:\n\n"
        "1. SYNTHESIS — Combine the key findings from all sources into a coherent summary\n"
        "2. KEY POINTS — List 5-10 most important findings\n"
        "3. METHODOLOGY — What research methods are common in this field?\n"
        "4. GAPS — What's missing from current research?\n"
        "5. RECOMMENDATIONS — What should a researcher focus on?\n"
        "6. SOURCES RATING — Rate the overall quality of sources (High/Medium/Low)\n\n"
        f"Sources:\n{sources_summary}\n\n"
        "Provide a comprehensive research brief."
    )

    analysis = run_tgpt(
        message=ai_prompt,
        provider=provider,
        system_prompt=f"You are analyzing research on: {query}",
        timeout=90,
    )

    if analysis:
        results["status"] = "ok"
        results["ai_analysis"] = analysis
        results["message"] = "Quick online research complete."
    else:
        results["status"] = "partial"
        results["ai_analysis"] = "AI analysis failed. Sources are still available for manual review."
        results["message"] = "Sources found but AI analysis unavailable."

    return results


def format_quick_report(result):
    """Format quick research result as readable text"""
    lines = []
    lines.append("=" * 80)
    lines.append(f"QUICK ONLINE RESEARCH REPORT".center(80))
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Query: {result.get('query', 'N/A')}")
    lines.append(f"Date: {result.get('timestamp', 'N/A')[:19]}")
    lines.append(f"Sources Found: {result.get('source_count', 0)}")
    lines.append(f"Status: {result.get('status', 'unknown')}")
    lines.append("")

    # Sources table
    sources = result.get("sources", [])
    if sources:
        lines.append("SOURCES")
        lines.append("-" * 78)
        for i, s in enumerate(sources[:20], 1):
            lines.append(f"  [{i}] {s.get('title', 'Untitled')}")
            lines.append(f"      Source: {s.get('source', '?')} | Type: {s.get('type', '?')} | Reliability: {s.get('reliability', '?')}")
            if s.get("url"):
                lines.append(f"      URL: {s['url']}")
            if s.get("snippet"):
                lines.append(f"      Summary: {s['snippet'][:150]}")
            lines.append("")

    # AI Analysis
    analysis = result.get("ai_analysis", "")
    if analysis:
        lines.append("")
        lines.append("=" * 80)
        lines.append("AI ANALYSIS".center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(analysis)

    lines.append("")
    lines.append("=" * 80)
    lines.append(f"End of Quick Research Report — ks-eye v{__import__('ks_eye').__version__}")
    lines.append("=" * 80)

    return "\n".join(lines)
