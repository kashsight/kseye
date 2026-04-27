"""
ks-eye v2.0 — Report Generation Engine
Takes the AI analysis + validation + sources and produces:
  • Summary (quick overview)
  • Full Report (comprehensive document)
  • Blog Post (engaging article)
  • Step-by-Step Guide
  • Research Proposal
All outputs are saved with citations, sources, and metadata.
"""

import json
import os
import time
from datetime import datetime

from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.engines.citation_manager import CitationManager
from ks_eye.engines.export_formats import (
    export_to_markdown, export_to_notion_obsidian, save_export
)
from ks_eye.engines.export_formatter import generate_html_report
from ks_eye.config import config
from ks_eye.ui import console, make_progress


# ── Output Generation Prompts ──

SUMMARY_PROMPT = """You are writing a concise executive summary.

Topic: {topic}

=== ANALYSIS ===
{analysis}
=== END ===

=== VALIDATION FEEDBACK ===
{validation}
=== END ===

Write a tight summary (500-800 words):
1. Main finding (1 paragraph)
2. Key evidence (3-5 bullet points)
3. What remains uncertain (1 paragraph)
4. Bottom line (1 paragraph)

Be precise, evidence-based, no fluff."""


REPORT_PROMPT = """You are writing a comprehensive research report.

Topic: {topic}

=== ANALYSIS ===
{analysis}
=== END ===

=== VALIDATION FEEDBACK ===
{validation}
=== END ===

Write a full report (2000-3000 words) with these sections:

1. EXECUTIVE SUMMARY (2 paragraphs)
2. BACKGROUND & CONTEXT (What readers need to know)
3. KEY FINDINGS (Numbered, with evidence for each)
4. DATA & STATISTICS (All numbers, percentages, research findings)
5. DIFFERENT PERSPECTIVES (Where experts disagree)
6. LIMITATIONS & UNCERTAINTIES (What we don't know)
7. CONCLUSIONS (Evidence-based, measured)
8. RECOMMENDATIONS (If applicable)

Use clear headings. Cite sources where possible. Professional tone."""


BLOG_PROMPT = """You are writing an engaging blog post about this topic.

Topic: {topic}

=== ANALYSIS ===
{analysis}
=== END ===

Write a blog post (1500-2000 words):
- Compelling headline (suggest 3 options)
- Hook paragraph that grabs attention
- Well-organized sections with headings
- Examples, stories, data to make it concrete
- Conversational but authoritative tone
- Clear conclusion with takeaway

Make it something people would actually want to read and share."""


GUIDE_PROMPT = """You are writing a step-by-step guide about this topic.

Topic: {topic}

=== ANALYSIS ===
{analysis}
=== END ===

Write a practical guide (1500-2000 words):
- What the reader needs to know first
- 8-12 clear steps (numbered, with explanations)
- Common mistakes to avoid
- Tips and best practices
- Resources for further learning

Clear, actionable, and thorough."""


PROPOSAL_PROMPT = """You are writing a research proposal based on this analysis.

Topic: {topic}

=== ANALYSIS ===
{analysis}
=== END ===

Write a research proposal (1500-2000 words):
1. Introduction & Problem Statement
2. Literature Review (from the analysis)
3. Research Questions (based on gaps identified)
4. Proposed Methodology
5. Expected Contributions
6. Timeline & Milestones

Academic tone, rigorous, well-structured."""


OUTPUT_WRITERS = {
    "summary": ("Executive Summary", SUMMARY_PROMPT),
    "report": ("Full Research Report", REPORT_PROMPT),
    "blog": ("Blog Post", BLOG_PROMPT),
    "guide": ("Step-by-Step Guide", GUIDE_PROMPT),
    "proposal": ("Research Proposal", PROPOSAL_PROMPT),
}


def generate_output(topic, analysis_text, validation_results, sources,
                    output_type="report", provider="sky"):
    """
    Generate a specific output type from analysis.

    Args:
        topic: Research topic
        analysis_text: The main analysis text from analyzer
        validation_results: Dict of validator outputs
        sources: List of source dicts from scraper
        output_type: 'summary', 'report', 'blog', 'guide', or 'proposal'
        provider: AI provider

    Returns:
        dict with output text, files, metadata
    """
    label, prompt_template = OUTPUT_WRITERS.get(output_type, OUTPUT_WRITERS["report"])

    console.print(f"\n[bold green]━━━ OUTPUT: Generating {label} ━━━[/bold green]")

    # Format validation feedback
    validation_text = ""
    if validation_results:
        parts = []
        for name, output in validation_results.items():
            parts.append(f"--- {name.upper()} ---")
            parts.append(output[:800])
            parts.append("")
        validation_text = "\n".join(parts)

    # Build prompt
    prompt = prompt_template.format(
        topic=topic,
        analysis=analysis_text[:15000],
        validation=validation_text[:5000],
    )

    # Generate
    with make_progress() as progress:
        task = progress.add_task(f"Writing {label}...", total=None)
        output_text = run_tgpt(prompt, provider, timeout=240)
        progress.update(task, completed=True)

    if not output_text or len(output_text) < 100:
        console.print("[yellow]⚠ Output generation returned empty. Retrying...[/yellow]")
        simple = f"Write a {label} about: {topic}\n\nBased on this analysis:\n{analysis_text[:8000]}"
        output_text = run_tgpt(simple, provider, timeout=240)

    if not output_text:
        return {"status": "failed", "output_text": "", "error": "Empty output"}

    console.print(f"[dim]  ✓ {label} generated ({len(output_text)} chars)[/dim]")

    return {
        "status": "complete",
        "output_type": output_type,
        "output_label": label,
        "output_text": output_text,
    }


def save_research_package(topic, output_results, sources, analysis,
                          validation_results, analysis_plan, provider):
    """
    Save the complete research package to disk.

    Creates a folder with:
      - final_output.txt (main output)
      - all_outputs.txt (all generated output types)
      - analysis.txt (AI analysis)
      - validation.txt (validation results)
      - sources.json (source metadata)
      - citations.txt (formatted citations)
      - metadata.json (session metadata)
      - output.html (HTML version)
      - output.md (Markdown version)
    """
    console.print(f"\n[bold green]━━━ SAVING: Research package ━━━[/bold green]")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:50]
    folder = os.path.join(config.RESEARCH_DIR, f"{safe_topic}_{ts}")
    os.makedirs(folder, exist_ok=True)

    # Find the primary output
    primary = output_results.get("primary") or next(iter(output_results.values()))
    primary_text = primary.get("output_text", "") if isinstance(primary, dict) else ""

    # Save primary output
    output_type = primary.get("output_type", "output") if isinstance(primary, dict) else "output"
    output_file = os.path.join(folder, f"final_{output_type}.txt")
    with open(output_file, "w") as f:
        f.write(f"{'=' * 80}\n")
        f.write(f"KS-EYE RESEARCH OUTPUT\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Output Type: {output_type}\n")
        f.write(f"Provider: {provider}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Sources: {len(sources)}\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(primary_text)

    # Save all outputs
    all_file = os.path.join(folder, "all_outputs.txt")
    with open(all_file, "w") as f:
        f.write(f"ALL GENERATED OUTPUTS: {topic}\n")
        f.write(f"{'=' * 80}\n\n")
        for name, result in output_results.items():
            if isinstance(result, dict) and result.get("output_text"):
                f.write(f"\n{'#' * 80}\n")
                f.write(f"# {result.get('output_label', name).upper()}\n")
                f.write(f"{'#' * 80}\n\n")
                f.write(result["output_text"])
                f.write("\n\n")

    # Save analysis
    analysis_file = os.path.join(folder, "analysis.txt")
    analysis_text = analysis.get("analysis", "") if isinstance(analysis, dict) else str(analysis)
    with open(analysis_file, "w") as f:
        f.write(f"AI ANALYSIS: {topic}\n{'=' * 80}\n\n")
        f.write(analysis_text)

    # Save validation
    if validation_results:
        val_file = os.path.join(folder, "validation.txt")
        with open(val_file, "w") as f:
            f.write(f"VALIDATION RESULTS: {topic}\n{'=' * 80}\n\n")
            for name, output in validation_results.items():
                f.write(f"\n{'─' * 60}\n")
                f.write(f"{name.upper()}\n")
                f.write(f"{'─' * 60}\n\n")
                f.write(output)
                f.write("\n\n")

    # Save sources
    sources_file = os.path.join(folder, "sources.json")
    with open(sources_file, "w") as f:
        json.dump(sources, f, indent=2, default=str)

    # Save citations
    cite_mgr = CitationManager()
    for source in sources:
        cite_mgr.add_reference(
            title=source.get("title", "Untitled"),
            url=source.get("url", ""),
            source_type=source.get("category", "web"),
            accessed=datetime.now().strftime("%Y-%m-%d"),
        )
    citations_file = os.path.join(folder, "citations.txt")
    with open(citations_file, "w") as f:
        f.write(f"CITATIONS: {topic}\n{'=' * 80}\n\n")
        f.write(cite_mgr.generate_bibliography())

    # Save metadata
    metadata = {
        "topic": topic,
        "provider": provider,
        "generated_at": datetime.now().isoformat(),
        "sources_total": len(sources),
        "sources_scraped": sum(1 for s in sources if s.get("scraped_content")),
        "output_types_generated": list(output_results.keys()),
        "analysis_chars": len(analysis_text) if analysis_text else 0,
        "folder": folder,
        "output_file": output_file,
        "all_outputs_file": all_file,
    }
    meta_file = os.path.join(folder, "metadata.json")
    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=2)

    # Generate HTML version
    try:
        html_text = generate_html_report(
            title=f"Research: {topic}",
            content=primary_text,
            sources=sources,
            metadata=metadata,
        )
        html_file = os.path.join(folder, "output.html")
        with open(html_file, "w") as f:
            f.write(html_text)
    except Exception:
        html_file = None

    # Generate Markdown version
    try:
        md_text = export_to_markdown(
            title=f"Research: {topic}",
            content=primary_text,
            metadata=metadata,
        )
        md_file = os.path.join(folder, "output.md")
        with open(md_file, "w") as f:
            f.write(md_text)
    except Exception:
        md_file = None

    # Save to session history
    config.save_session(metadata)

    # Summary
    console.print(f"[dim]  ✓ Saved to: {folder}/[/dim]")
    console.print(f"[dim]    • final_{output_type}.txt (primary output)")
    console.print(f"[dim]    • all_outputs.txt (all generated versions)")
    console.print(f"[dim]    • analysis.txt (AI analysis)")
    if validation_results:
        console.print(f"[dim]    • validation.txt (credibility checks)")
    console.print(f"[dim]    • sources.json (source metadata)")
    console.print(f"[dim]    • citations.txt (formatted citations)")
    console.print(f"[dim]    • metadata.json")
    if html_file:
        console.print(f"[dim]    • output.html")
    if md_file:
        console.print(f"[dim]    • output.md")

    return {
        "folder": folder,
        "output_file": output_file,
        "all_outputs_file": all_file,
        "html_file": html_file,
        "md_file": md_file,
        "citations_file": citations_file,
        "metadata_file": meta_file,
    }
