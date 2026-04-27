"""
ks-eye v2.0 — Analysis Engine
AI reads all scraped data and produces structured analysis.
Multi-agent validation phase runs here.
"""

import json
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.engines.citation_manager import CitationManager
from ks_eye.config import config
from ks_eye.ui import console, make_progress


# ═══════════════════════════════════════════════════════════
#  PHASE 1: AI READS SCRAPED DATA → SUMMARY
# ═══════════════════════════════════════════════════════════

READ_DATA_SYSTEM = """You are a Research Analyst. You have been given scraped web content
from multiple real sources about a specific topic.

Your task: Read ALL the content carefully and produce a comprehensive
analysis. This is NOT a summary — this is a deep analysis.

Structure your response as:

EXECUTIVE SUMMARY
(2-3 paragraphs: what the data shows, overall picture)

KEY FINDINGS
(Numbered list of 8-12 major findings. Each finding: 2-4 sentences.
Include specific data, numbers, names where available.)

EVIDENCE ASSESSMENT
(For each major finding, note the strength of evidence:
Strong / Moderate / Weak — and why)

CONTRADICTIONS & UNCERTAINTIES
(Where do sources disagree? What is uncertain or contested?)

CONTEXT & BACKGROUND
(What background knowledge is needed to understand this topic?)

DATA & STATISTICS
(All numerical data, percentages, research findings extracted
from the sources in a structured format)

PERSPECTIVES & VIEWPOINTS
(Different schools of thought, stakeholder positions, cultural/regional differences)

Be thorough, analytical, and evidence-based. Cite source numbers when making claims."""


def analyze_scraped_data(topic, sources, analysis_plan=None, provider="sky"):
    """
    AI reads all scraped content and produces structured analysis.

    Args:
        topic: Research topic
        sources: List of source dicts from scraper (with scraped_content)
        analysis_plan: Optional dict from prompt_rewriter
        provider: AI provider

    Returns:
        dict with analysis text, metadata
    """
    console.print(f"\n[bold green]━━━ ANALYSIS: AI reads content ━━━[/bold green]")

    # Check if we're using AI knowledge fallback
    is_ai_fallback = any(s.get("source_type") == "ai_knowledge" for s in sources)

    if is_ai_fallback:
        console.print(f"[dim]  📚 Using AI internal knowledge base as source[/dim]")
    else:
        scraped = [s for s in sources if s.get("scraped_content")]
        snippets_only = [s for s in sources if not s.get("scraped_content") and s.get("snippet")]
        console.print(f"  Sources with full content: {len(scraped)}")
        console.print(f"  Sources with snippets only: {len(snippets_only)}")

    # Build analysis context text
    context_parts = []
    for i, source in enumerate(sources, 1):
        content = source.get("scraped_content") or source.get("snippet") or ""
        if len(content) < 30:
            continue
        source_label = source.get("title", "Untitled")
        source_note = " [AI Knowledge]" if source.get("source_type") == "ai_knowledge" else ""
        context_parts.append(f"=== SOURCE #{i}{source_note} ===")
        context_parts.append(f"Title: {source_label}")
        context_parts.append(f"URL: {source.get('url', 'Unknown')}")
        context_parts.append(f"Category: {source.get('category', 'general')}")
        context_parts.append(f"---")
        # Cap individual source content to avoid context overflow
        context_parts.append(content[:5000])
        context_parts.append(f"=== END SOURCE #{i} ===\n")

    full_context = "\n".join(context_parts)

    if not full_context.strip():
        console.print("[yellow]⚠ No content available to analyze[/yellow]")
        return {
            "analysis": "No content was successfully scraped or available for analysis.",
            "status": "empty",
        }

    # Build the prompt — different for AI knowledge vs web sources
    if is_ai_fallback:
        # For AI knowledge, just format and expand
        prompt_parts = [
            f"RESEARCH TOPIC: {topic}",
            "",
            "The following is AI-generated research from internal knowledge.",
            "Expand, structure, and deepen this analysis significantly.",
            "Add more evidence, counter-arguments, statistics, and nuance.",
            "",
            full_context,
        ]
        system_prompt = "You are a senior research analyst. Take this initial research and expand it into a comprehensive, well-structured analysis with multiple sections."
    else:
        # For web sources, analyze the scraped content
        prompt_parts = [
            f"RESEARCH TOPIC: {topic}",
            "",
            "Below is the complete scraped content from all sources. Analyze it thoroughly.",
            "",
            full_context,
        ]
        system_prompt = READ_DATA_SYSTEM

    if analysis_plan and analysis_plan.get("raw_plan"):
        prompt_parts.append("")
        prompt_parts.append("=== ANALYSIS PLAN (follow this structure) ===")
        prompt_parts.append(analysis_plan["raw_plan"])
        prompt_parts.append("=== END ANALYSIS PLAN ===")

    prompt = "\n".join(prompt_parts)

    # Run analysis
    console.print(f"\n[dim]  🤖 AI is analyzing...[/dim]")
    start = time.time()

    with make_progress() as progress:
        task = progress.add_task("Analyzing...", total=None)
        analysis_text = run_tgpt(prompt, provider, system_prompt=system_prompt, timeout=300)
        progress.update(task, completed=True)

    elapsed = time.time() - start

    if not analysis_text or len(analysis_text) < 100:
        console.print("[yellow]⚠ AI returned a weak or empty analysis, retrying...[/yellow]")
        # Retry with simpler prompt
        simple_prompt = f"Analyze the following scraped research data about: {topic}\n\n{full_context[:10000]}\n\nProvide a comprehensive analysis with key findings, evidence, and conclusions."
        analysis_text = run_tgpt(simple_prompt, provider, timeout=300)

    if not analysis_text:
        return {
            "analysis": "Analysis failed — AI could not process the scraped data.",
            "status": "failed",
            "elapsed": elapsed,
        }

    console.print(f"[dim]  ✓ Analysis complete ({len(analysis_text)} chars, {elapsed:.1f}s)[/dim]")

    return {
        "analysis": analysis_text,
        "status": "complete",
        "sources_analyzed": len(sources),
        "total_content_chars": len(full_context),
        "elapsed_seconds": round(elapsed, 1),
    }


# ═══════════════════════════════════════════════════════════
#  PHASE 2: MULTI-AGENT VALIDATION
# ═══════════════════════════════════════════════════════════

VALIDATOR_PROMPTS = {
    "credibility": (
        "Review this research analysis for credibility.\n\n"
        "Topic: {topic}\n\n"
        "=== ANALYSIS ===\n{analysis}\n=== END ===\n\n"
        "Rate credibility 1-10. Flag unsupported claims, weak reasoning."
    ),
    "bias": (
        "Review this analysis for bias.\n\n"
        "Topic: {topic}\n\n"
        "=== ANALYSIS ===\n{analysis}\n=== END ===\n\n"
        "Identify selection bias, framing bias, missing perspectives."
    ),
    "completeness": (
        "What is MISSING from this analysis?\n\n"
        "Topic: {topic}\n\n"
        "=== ANALYSIS ===\n{analysis}\n=== END ===\n\n"
        "Identify gaps, blind spots, unaddressed angles."
    ),
    "fact_check": (
        "Fact-check the claims in this analysis.\n\n"
        "Topic: {topic}\n\n"
        "=== ANALYSIS ===\n{analysis}\n=== END ===\n\n"
        "For each major claim: is it verifiable? Is it accurate? Flag anything dubious."
    ),
    "consistency": (
        "Check for internal contradictions.\n\n"
        "Topic: {topic}\n\n"
        "=== ANALYSIS ===\n{analysis}\n=== END ===\n\n"
        "Do any parts contradict each other? List every inconsistency."
    ),
}


def validate_analysis(topic, analysis_text, provider="sky"):
    """
    Run 5 validation agents in parallel against the analysis.

    Returns:
        dict with validation reports per agent
    """
    console.print(f"\n[bold green]━━━ VALIDATION: 5-agent credibility check ━━━[/bold green]")

    results = {}

    def run_validator(name, prompt_template):
        prompt = prompt_template.format(topic=topic, analysis=analysis_text[:12000])
        output = run_tgpt(prompt, provider, timeout=60)
        return name, output or f"[Validator {name} returned empty]"

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(run_validator, name, tmpl): name
            for name, tmpl in VALIDATOR_PROMPTS.items()
        }
        for future in as_completed(futures):
            name, output = future.result()
            results[name] = output
            icon = "✓" if len(output) > 20 else "⚠"
            console.print(f"      {icon} {name}")

    return results


# ═══════════════════════════════════════════════════════════
#  PHASE 3: CITATION EXTRAION
# ═══════════════════════════════════════════════════════════

def extract_citations(sources, analysis_text):
    """
    Build a citation list from the sources that were actually used.
    Returns a list of citation dicts.
    """
    citations = []
    cite_mgr = CitationManager()

    for i, source in enumerate(sources, 1):
        content = source.get("scraped_content") or source.get("snippet") or ""
        # Check if this source's content appears in the analysis
        if content[:100] and content[:100] in analysis_text:
            citation = cite_mgr.add_reference(
                title=source.get("title", "Untitled"),
                url=source.get("url", ""),
                source_type=source.get("category", "web"),
                accessed=datetime.now().strftime("%Y-%m-%d"),
            )
            citations.append(citation)

    # Also try to auto-detect from analysis text
    if len(citations) < 3 and analysis_text:
        auto_citations = cite_mgr.add_references_from_text(analysis_text)
        for c in auto_citations:
            if c not in citations:
                citations.append(c)

    return citations


# ═══════════════════════════════════════════════════════════
#  CONFIDENCE SCORES
# ═══════════════════════════════════════════════════════════

CONFIDENCE_PROMPT = """You are a Confidence Scorer. Given research analysis:

TOPIC: {topic}

=== ANALYSIS ===
{analysis}
=== END ===

For EACH major finding/claim in the analysis, assign a confidence score:
- HIGH: Strong evidence, multiple sources agree, well-established
- MEDIUM: Some evidence, limited sources, reasonable but not certain
- LOW: Speculative, single source, contested, or preliminary

Format:
1. [HIGH/MEDIUM/LOW] Claim summary — Why
2. [HIGH/MEDIUM/LOW] Claim summary — Why
...

End with an overall research quality score: 1-10"""


def generate_confidence_scores(topic, analysis_text, provider="sky"):
    """Generate confidence scores for all major claims."""
    prompt = CONFIDENCE_PROMPT.format(
        topic=topic,
        analysis=analysis_text[:10000],
    )
    result = run_tgpt(prompt, provider, timeout=90)
    return result if result else "Confidence scoring failed."
