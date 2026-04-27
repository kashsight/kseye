"""
ks-eye v2.0 — Clean CLI
Online AI Research Platform

Commands:
  kseye                     → Interactive menu
  kseye run "topic"         → Full research: scrape → analyze → report
  kseye scrape "topic"      → Scrape only (no analysis)
  kseye quick "topic"       → Fast one-shot research
  kseye config              → Configure providers/API keys
  kseye version             → Version info
"""

import sys
import json
import os
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ks_eye import __version__
from ks_eye.ui import (
    console, banner, show_success, show_error, show_warning, show_info,
    prompt_user, confirm, show_section, make_progress, display_table,
)
from ks_eye.config import config
from ks_eye.engines.tgpt_engine import check_tgpt_installed, save_api_key
from ks_eye.engines.scraper import scrape_topic
from ks_eye.engines.prompt_rewriter import rewrite_for_search, rewrite_for_analysis
from ks_eye.engines.analyzer import analyze_scraped_data, validate_analysis
from ks_eye.engines.reporter import generate_output, save_research_package
from ks_eye.engines.multi_agent import multi_agent_research
from ks_eye.engines.comparative import comparative_research
from ks_eye.engines.factcheck import fact_check
from ks_eye.engines.timeline import build_timeline
from ks_eye.engines.opposing_views import opposing_views
from ks_eye.engines.batch_research import batch_research
from ks_eye.engines.research_utils import (
    generate_follow_ups, compare_versions, search_research_history,
    list_all_tags, tag_session, get_notes, add_note,
    list_templates, get_template,
)
from ks_eye.engines.analyzer import generate_confidence_scores

console = Console()


# ═══════════════════════════════════════════════════════════
#  CLI ENTRY
# ═══════════════════════════════════════════════════════════

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """ks-eye v2.0 — Online AI Research Platform"""
    if ctx.invoked_subcommand is None:
        interactive_menu()


@main.command()
def version():
    """Show version and AI status"""
    has_ai = check_tgpt_installed()
    mode = "[green]● Online AI ready[/green]" if has_ai else "[red]● AI not installed[/red]"
    console.print(f"\n[bold cyan]ks-eye[/bold cyan] v{__version__} — {mode}")
    if not has_ai:
        console.print("\n[dim]Install tgpt: go install github.com/aikooo/tgpt/v2@latest[/dim]")


# ═══════════════════════════════════════════════════════════
#  RUN — Full Research Pipeline
# ═══════════════════════════════════════════════════════════

@main.command()
@click.argument("topic", required=False)
@click.option("-o", "--output", type=click.Choice(["summary", "report", "blog", "guide", "proposal"]),
              default="report", help="Output type")
@click.option("-d", "--depth", type=int, default=2, help="Scrape depth: 1=quick, 2=standard, 3=deep")
@click.option("-p", "--provider", default=None, help="AI provider")
@click.option("-m", "--multi-agent", is_flag=True, help="Use 45-agent pipeline instead")
def run(topic, output, depth, provider, multi_agent):
    """Full research pipeline: Scrape → AI reads → Report"""
    if not check_tgpt_installed():
        show_error("tgpt not installed. Run: go install github.com/aikooo/tgpt/v2@latest")
        sys.exit(1)

    provider = provider or config.get("default_provider", "sky")

    # Interactive if no topic given
    if not topic:
        console.print(banner())
        show_section("Full Research Pipeline")
        topic = prompt_user("Research topic")
        if not topic:
            show_error("Topic required.")
            return

        # Confirm settings
        console.print(f"\n  Output type: [bold]{output}[/bold]")
        console.print(f"  Scrape depth: [bold]{depth}[/bold]")
        console.print(f"  Provider: [bold]{provider}[/bold]\n")

    console.print(f"\n[bold]🔍 Researching:[/bold] {topic}")
    console.print(f"[dim]  Mode: {'45-agent pipeline' if multi_agent else 'Standard pipeline'}[/dim]")
    console.print(f"[dim]  Output: {output} | Depth: {depth} | Provider: {provider}[/dim]\n")

    if multi_agent:
        # ── 45-Agent Pipeline ──
        result = multi_agent_research(topic, output_type=output, provider=provider)
    else:
        # ── Standard Pipeline ──
        result = _standard_pipeline(topic, output, depth, provider)

    if result and result.get("status") == "complete":
        console.print(f"\n[bold green]✓ Research complete → {result.get('output_file', 'see folder')}[/bold green]")


# ═══════════════════════════════════════════════════════════
#  SCRAPE — Scrape Only
# ═══════════════════════════════════════════════════════════

@main.command()
@click.argument("topic", required=False)
@click.option("-d", "--depth", type=int, default=2, help="Scrape depth: 1=quick, 2=standard, 3=deep")
@click.option("-p", "--provider", default=None, help="AI provider for search")
def scrape(topic, depth, provider):
    """Scrape real websites without analysis"""
    provider = provider or config.get("default_provider", "sky")

    if not topic:
        console.print(banner())
        show_section("Web Scraper")
        topic = prompt_user("Research topic")
        if not topic:
            show_error("Topic required.")
            return

    result = scrape_topic(topic, depth=depth, provider=provider)

    # Show summary table
    console.print(f"\n[bold]Sources by category:[/bold]")
    rows = []
    for cat, count in sorted(result["categories"].items()):
        rows.append([cat, str(count)])
    rows.append(["TOTAL", str(result["total_sources"])])
    display_table(["Category", "Count"], rows)


# ═══════════════════════════════════════════════════════════
#  QUICK — Fast One-Shot
# ═══════════════════════════════════════════════════════════

@main.command()
@click.argument("topic", required=False)
@click.option("-p", "--provider", default=None, help="AI provider")
def quick(topic, provider):
    """Fast one-shot research (scrape + summary in one go)"""
    if not check_tgpt_installed():
        show_error("tgpt not installed. Run: go install github.com/aikooo/tgpt/v2@latest")
        sys.exit(1)

    provider = provider or config.get("default_provider", "sky")

    if not topic:
        console.print(banner())
        show_section("Quick Research")
        topic = prompt_user("Research topic")
        if not topic:
            show_error("Topic required.")
            return

    # Quick scrape (depth 1)
    scrape_result = scrape_topic(topic, depth=1, provider=provider)

    if scrape_result["scraped_count"] == 0:
        show_error("No content could be scraped.")
        return

    # Quick analysis
    from ks_eye.engines.tgpt_engine import run_tgpt
    all_content = "\n\n".join(
        f"--- {s['title']} ---\n{s.get('scraped_content') or s.get('snippet', '')}"
        for s in scrape_result["sources"][:10]
        if s.get("scraped_content") or s.get("snippet")
    )

    prompt = (
        f"Provide a comprehensive research summary about: {topic}\n\n"
        f"Based on these sources:\n\n{all_content[:12000]}\n\n"
        f"Include: key findings, evidence, different perspectives, and conclusions.\n"
        f"Be thorough and evidence-based."
    )

    console.print(f"\n[bold green]━━━ QUICK ANALYSIS ━━━[/bold green]")
    analysis = run_tgpt(prompt, provider, timeout=180)

    if analysis:
        from rich.panel import Panel
        console.print(Panel(analysis[:2000], title=f"Quick Research: {topic}", border_style="green"))

        # Save
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = "".join(c if c.isalnum() else "_" for c in topic)[:50]
        folder = os.path.join(config.RESEARCH_DIR, f"quick_{safe}_{ts}")
        os.makedirs(folder, exist_ok=True)

        out_file = os.path.join(folder, "quick_research.txt")
        with open(out_file, "w") as f:
            f.write(f"QUICK RESEARCH: {topic}\n{'=' * 80}\n\n")
            f.write(analysis)

        console.print(f"\n[dim]  Saved: {out_file}[/dim]")


# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════

@main.command()
def config_cmd():
    """Configure providers and API keys"""
    console.print(banner())
    show_section("Configuration")

    console.print(Panel(
        "[bold cyan]1[/bold cyan].   Set default AI provider\n"
        "[bold cyan]2[/bold cyan].   Set API key for a provider\n"
        "[bold cyan]3[/bold cyan].   View current settings\n"
        "[bold cyan]4[/bold cyan].   Browse research history\n"
        "[bold cyan]0[/bold cyan].   Exit",
        title=" Config Menu",
        border_style="cyan",
    ))

    choice = prompt_user("Select", "3")

    if choice == "1":
        from ks_eye import AVAILABLE_PROVIDERS
        console.print("\nAvailable providers:")
        for i, p in enumerate(AVAILABLE_PROVIDERS, 1):
            default = " (current)" if p == config.get("default_provider") else ""
            console.print(f"  {i}. {p}{default}")
        idx = prompt_user("Provider number")
        if idx.isdigit() and 1 <= int(idx) <= len(AVAILABLE_PROVIDERS):
            config.set("default_provider", AVAILABLE_PROVIDERS[int(idx) - 1])
            show_success(f"Default provider set to {AVAILABLE_PROVIDERS[int(idx) - 1]}")

    elif choice == "2":
        provider = prompt_user("Provider name (sky, openai, gemini, etc.)")
        key = prompt_user("API key")
        if provider and key:
            save_api_key(provider, key)
            show_success(f"API key saved for {provider}")

    elif choice == "3":
        console.print("\n[bold]Current Settings:[/bold]")
        for key, val in config.get_all().items():
            if key not in ("research_sessions",):
                console.print(f"  {key}: [dim]{val}[/dim]")

    elif choice == "4":
        sessions = config.get("research_sessions", [])
        if sessions:
            console.print(f"\n[bold]Research History ({len(sessions)} sessions):[/bold]\n")
            rows = []
            for s in sessions[-20:]:
                rows.append([
                    s.get("timestamp", "?")[:19],
                    s.get("topic", "?")[:40],
                    s.get("output_type", s.get("type", "?"))[:15],
                ])
            display_table(["Date", "Topic", "Type"], rows)
        else:
            show_info("No research sessions yet.")


# ═══════════════════════════════════════════════════════════
#  INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════

def interactive_menu():
    """Main interactive menu."""
    console.print(banner())

    has_ai = check_tgpt_installed()
    if not has_ai:
        show_warning("tgpt not installed. AI features won't work. Install: go install github.com/aikooo/tgpt/v2@latest")

    console.print(Panel(
        "[bold cyan]1[/bold cyan].   🔬 Full Research     (scrape → analyze → report)\n"
        "[bold cyan]2[/bold cyan].   🌐 Scrape Only        (fetch real websites)\n"
        "[bold cyan]3[/bold cyan].   ⚡ Quick Research     (fast one-shot)\n"
        "[bold cyan]4[/bold cyan].   🏢 Multi-Agent        (45 agents)\n"
        "[bold cyan]5[/bold cyan].   ⚖️  Comparative        (topic A vs topic B)\n"
        "[bold cyan]6[/bold cyan].   🔍 Fact-Check         (verify claims)\n"
        "[bold cyan]7[/bold cyan].   📅 Timeline           (chronological events)\n"
        "[bold cyan]8[/bold cyan].   ⚖️  Opposing Views     (both sides of debate)\n"
        "[bold cyan]9[/bold cyan].   📦 Batch Research     (multiple topics)\n"
        "[bold cyan]10[/bold cyan].  📋 Templates          (pre-built workflows)\n"
        "[bold cyan]11[/bold cyan].  🔎 Search History     (find past research)\n"
        "[bold cyan]12[/bold cyan].  🏷️  Tags              (organize research)\n"
        "[bold cyan]13[/bold cyan].  ⚙️  Config            (providers, API keys)\n"
        "[bold cyan]0[/bold cyan].   Exit",
        title=" Main Menu",
        border_style="cyan",
    ))

    choice = prompt_user("Select", "1")

    if choice == "0":
        console.print("[dim]Goodbye![/dim]")
        return
    elif choice == "1":
        _interactive_full_research()
    elif choice == "2":
        _interactive_scrape()
    elif choice == "3":
        _interactive_quick()
    elif choice == "4":
        _interactive_multi_agent()
    elif choice == "5":
        _interactive_comparative()
    elif choice == "6":
        _interactive_factcheck()
    elif choice == "7":
        _interactive_timeline()
    elif choice == "8":
        _interactive_opposing_views()
    elif choice == "9":
        _interactive_batch()
    elif choice == "10":
        _interactive_templates()
    elif choice == "11":
        _interactive_search()
    elif choice == "12":
        _interactive_tags()
    elif choice == "13":
        _run_config()
    else:
        show_error("Invalid choice.")


def _interactive_full_research():
    """Interactive full research pipeline."""
    show_section("Full Research Pipeline")
    topic = prompt_user("Research topic")
    if not topic:
        return

    console.print("\n[dim]Output types:[/dim]")
    console.print("  1. Summary   (concise overview)")
    console.print("  2. Report    (comprehensive — default)")
    console.print("  3. Blog Post (engaging article)")
    console.print("  4. Guide     (step-by-step)")
    console.print("  5. Proposal  (research proposal)")
    output_map = {"1": "summary", "2": "report", "3": "blog", "4": "guide", "5": "proposal"}
    out_choice = prompt_user("Output type (1-5)", "2")
    output_type = output_map.get(out_choice, "report")

    console.print("\n[dim]Scrape depth:[/dim]")
    console.print("  1. Quick  (5 sources)")
    console.print("  2. Standard (15 sources — default)")
    console.print("  3. Deep   (30 sources + academic)")
    depth_map = {"1": 1, "2": 2, "3": 3}
    depth_choice = prompt_user("Depth (1-3)", "2")
    depth = depth_map.get(depth_choice, 2)

    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")

    result = _standard_pipeline(topic, output_type, depth, provider)
    if result and result.get("status") == "complete":
        show_success(f"Saved to {result['folder']}")


def _interactive_scrape():
    """Interactive scrape only."""
    show_section("Web Scraper")
    topic = prompt_user("Research topic")
    if not topic:
        return
    depth = int(prompt_user("Depth 1-3", "2"))
    result = scrape_topic(topic, depth=depth)
    show_success(f"Scraped {result['scraped_count']} sources → {result['folder']}")


def _interactive_quick():
    """Interactive quick research."""
    show_section("Quick Research")
    topic = prompt_user("Research topic")
    if not topic:
        return
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    # Run quick research directly
    if not check_tgpt_installed():
        show_error("tgpt not installed. Run: go install github.com/aikooo/tgpt/v2@latest")
        return
    from ks_eye.engines.scraper import scrape_topic
    from ks_eye.engines.tgpt_engine import run_tgpt
    scrape_result = scrape_topic(topic, depth=1, provider=provider)
    if scrape_result["scraped_count"] == 0:
        show_error("No content could be scraped.")
        return
    all_content = "\n\n".join(
        f"--- {s['title']} ---\n{s.get('scraped_content') or s.get('snippet', '')}"
        for s in scrape_result["sources"][:10]
        if s.get("scraped_content") or s.get("snippet")
    )
    prompt_text = (
        f"Provide a comprehensive research summary about: {topic}\n\n"
        f"Based on these sources:\n\n{all_content[:12000]}\n\n"
        f"Include: key findings, evidence, different perspectives, and conclusions."
    )
    console.print(f"\n[bold green]━━━ QUICK ANALYSIS ━━━[/bold green]")
    analysis = run_tgpt(prompt_text, provider, timeout=180)
    if analysis:
        from rich.panel import Panel
        console.print(Panel(analysis[:2000], title=f"Quick Research: {topic}", border_style="green"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = "".join(c if c.isalnum() else "_" for c in topic)[:50]
        folder = os.path.join(config.RESEARCH_DIR, f"quick_{safe}_{ts}")
        os.makedirs(folder, exist_ok=True)
        out_file = os.path.join(folder, "quick_research.txt")
        with open(out_file, "w") as f:
            f.write(f"QUICK RESEARCH: {topic}\n{'=' * 80}\n\n{analysis}")
        console.print(f"\n[dim]  Saved: {out_file}[/dim]")


def _interactive_multi_agent():
    """Interactive multi-agent research."""
    show_section("Multi-Agent Research (45 agents)")
    topic = prompt_user("Research topic")
    if not topic:
        return
    output_map = {"1": "summary", "2": "report", "3": "blog", "4": "guide", "5": "proposal"}
    console.print("  1. Summary  2. Report  3. Blog  4. Guide  5. Proposal")
    out_choice = prompt_user("Output type (1-5)", "2")
    output_type = output_map.get(out_choice, "report")
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    result = multi_agent_research(topic, output_type=output_type, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Saved to {result['folder']}")


def _run_config():
    """Run config interactively."""
    config_cmd.invoke(None)


def _browse_history():
    """Browse research history."""
    sessions = config.get("research_sessions", [])
    if not sessions:
        show_info("No research sessions yet. Run some research first!")
        return

    console.print(f"\n[bold]Research History ({len(sessions)} sessions):[/bold]\n")
    rows = []
    for s in sessions[-30:]:
        rows.append([
            s.get("timestamp", "?")[:19],
            s.get("topic", "?")[:40],
            s.get("output_type", s.get("type", "?"))[:15],
            s.get("folder", "")[-40:],
        ])
    display_table(["Date", "Topic", "Type", "Folder"], rows)

    # Option to open one
    console.print(f"\n[dim]Enter a folder path to view, or blank to return[/dim]")
    path = prompt_user("Folder path")
    if path and os.path.isdir(path):
        console.print(f"\n[dim]Contents of {path}:[/dim]")
        for f in sorted(os.listdir(path)):
            fpath = os.path.join(path, f)
            size = os.path.getsize(fpath)
            console.print(f"  {f} ({size:,} bytes)")

        # Preview option
        preview = prompt_user("File to preview")
        if preview:
            fpath = os.path.join(path, preview)
            if os.path.isfile(fpath):
                with open(fpath, "r") as f:
                    content = f.read()
                from rich.panel import Panel
                console.print(Panel(content[:3000], title=preview, border_style="cyan"))


# ═══════════════════════════════════════════════════════════
#  STANDARD PIPELINE (the main workflow)
# ═══════════════════════════════════════════════════════════

def _standard_pipeline(topic, output_type, depth, provider):
    """
    Standard research pipeline:
    1. AI rewrites topic → optimized search queries
    2. AI creates analysis plan
    3. Scrape real websites using optimized queries
    4. AI reads all scraped content → analysis
    5. Multi-agent validation (5 agents)
    6. Generate output (summary/report/blog/guide/proposal)
    7. Save everything
    """

    # ── Step 1: AI rewrites topic ──
    show_section("STEP 1: AI Understanding Your Topic")
    search_queries = rewrite_for_search(topic)
    analysis_plan = rewrite_for_analysis(topic)

    console.print(f"\n[dim]  AI-optimized search queries:[/dim]")
    for i, q in enumerate(search_queries[:5], 1):
        console.print(f"    {i}. {q}")

    # ── Step 2: Scrape ──
    show_section("STEP 2: Scraping Real Websites")
    scrape_result = scrape_topic(topic, depth=depth, provider=provider)

    if scrape_result["scraped_count"] == 0:
        show_error("No content scraped. Cannot proceed.")
        return {"status": "failed", "error": "No content scraped"}

    # ── Step 3: AI Analysis ──
    show_section("STEP 3: AI Reads & Analyzes All Content")
    analysis = analyze_scraped_data(
        topic,
        scrape_result["sources"],
        analysis_plan=analysis_plan,
        provider=provider,
    )

    if analysis.get("status") != "complete":
        show_error("Analysis failed.")
        return {"status": "failed", "error": "Analysis failed"}

    # ── Step 4: Validation ──
    show_section("STEP 4: 5-Agent Validation")
    validation = validate_analysis(topic, analysis["analysis"], provider=provider)

    # ── Step 5: Generate Output ──
    show_section("STEP 5: Generating Output")
    output_result = generate_output(
        topic,
        analysis["analysis"],
        validation,
        scrape_result["sources"],
        output_type=output_type,
        provider=provider,
    )

    if output_result.get("status") != "complete":
        show_error("Output generation failed.")
        return {"status": "failed", "error": "Output generation failed"}

    # ── Step 6: Save Everything ──
    show_section("STEP 6: Saving Research Package")
    output_results = {"primary": output_result}
    save_result = save_research_package(
        topic, output_results, scrape_result["sources"],
        analysis, validation, analysis_plan, provider,
    )

    return {
        "status": "complete",
        "topic": topic,
        "output_type": output_type,
        "folder": save_result["folder"],
        "output_file": save_result["output_file"],
        "sources_scraped": scrape_result["scraped_count"],
        "analysis_chars": len(analysis["analysis"]),
    }


# ═══════════════════════════════════════════════════════════
#  NEW FEATURE HANDLERS
# ═══════════════════════════════════════════════════════════

def _interactive_comparative():
    """Interactive comparative research (A vs B)."""
    show_section("Comparative Research — A vs B")
    topic_a = prompt_user("Topic A")
    if not topic_a:
        return
    topic_b = prompt_user("Topic B")
    if not topic_b:
        return
    depth = int(prompt_user("Scrape depth (1-3)", "2"))
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    result = comparative_research(topic_a, topic_b, depth=depth, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Saved to {result['folder']}")


def _interactive_factcheck():
    """Interactive fact-checking."""
    show_section("Fact-Check Engine")
    console.print("[dim]Enter claims to check (one per line). End with empty line:[/dim]")
    claims = []
    while True:
        line = prompt_user(f"Claim {len(claims)+1}")
        if not line:
            break
        claims.append(line)
    if not claims:
        show_error("No claims entered.")
        return
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    result = fact_check("\n".join(claims), provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Saved to {result['folder']}")


def _interactive_timeline():
    """Interactive timeline builder."""
    show_section("Timeline Builder")
    topic = prompt_user("Research topic")
    if not topic:
        return
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    result = build_timeline(topic, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Saved to {result['folder']}")


def _interactive_opposing_views():
    """Interactive opposing views research."""
    show_section("Opposing Views — Both Sides of a Debate")
    topic = prompt_user("Controversial topic")
    if not topic:
        return
    side_a = prompt_user("Side A label (e.g., Proponents)", "Supporters")
    side_b = prompt_user("Side B label (e.g., Critics)", "Critics")
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    result = opposing_views(topic, side_a_label=side_a, side_b_label=side_b, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Saved to {result['folder']}")


def _interactive_batch():
    """Interactive batch research."""
    show_section("Batch Research — Multiple Topics")
    console.print("[dim]Enter topics (one per line). End with empty line:[/dim]")
    topics = []
    while True:
        line = prompt_user(f"Topic {len(topics)+1}")
        if not line:
            break
        topics.append(line)
    if not topics:
        show_error("No topics entered.")
        return
    provider = prompt_user(f"Provider (default: {config.get('default_provider', 'sky')})", "")
    if not provider:
        provider = config.get("default_provider", "sky")
    result = batch_research(topics, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Done: {result['successful']}/{len(topics)} completed")


def _interactive_templates():
    """Show and use research templates."""
    show_section("Research Templates")
    templates = list_templates()
    console.print("\n[bold]Available Templates:[/bold]\n")
    rows = []
    for name, tmpl in templates.items():
        rows.append([name, tmpl["name"], tmpl["description"]])
    display_table(["ID", "Name", "Description"], rows)

    console.print(f"\n[dim]Enter template name to use (or blank to return)[/dim]")
    tmpl_name = prompt_user("Template")
    if tmpl_name:
        tmpl = get_template(tmpl_name)
        if tmpl:
            console.print(f"\n[bold]{tmpl['name']}[/bold]: {tmpl['description']}")
            console.print(f"[dim]{tmpl['prompt_additions']}[/dim]\n")
            # Start research with this template
            topic = prompt_user("Research topic")
            if topic:
                provider = prompt_user(f"Provider", config.get("default_provider", "sky"))
                result = _standard_pipeline(topic, "report", 2, provider)
                if result:
                    show_success(f"Saved to {result['folder']}")


def _interactive_search():
    """Search research history."""
    show_section("Search Research History")
    query = prompt_user("Search query")
    if not query:
        return
    results = search_research_history(query)
    if results:
        console.print(f"\n[bold]Found {len(results)} results:[/bold]\n")
        rows = []
        for r in results:
            rows.append([
                str(r.get("score", 0)),
                r.get("topic", "?")[:40],
                r.get("match", ""),
                r.get("timestamp", "")[:19],
            ])
        display_table(["Score", "Topic", "Match", "Date"], rows)
    else:
        show_info("No results found.")


def _interactive_tags():
    """Tag and browse research."""
    show_section("Tags & Organization")
    console.print(Panel(
        "[bold cyan]1[/bold cyan].   View all tags\n"
        "[bold cyan]2[/bold cyan].   Tag a research session\n"
        "[bold cyan]3[/bold cyan].   View notes on a session\n"
        "[bold cyan]4[/bold cyan].   Add note to a session\n"
        "[bold cyan]0[/bold cyan].   Go back",
        title=" Tags Menu",
        border_style="cyan",
    ))
    choice = prompt_user("Select", "1")

    if choice == "1":
        tags = list_all_tags()
        if tags:
            rows = [[t, str(c)] for t, c in tags.items()]
            display_table(["Tag", "Count"], rows)
        else:
            show_info("No tags yet. Tag some research first!")

    elif choice == "2":
        folder = prompt_user("Research folder path")
        if folder and os.path.isdir(folder):
            tags_input = prompt_user("Tags (comma-separated)")
            if tags_input:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                tag_session(folder, tags)
                show_success(f"Tags added: {', '.join(tags)}")

    elif choice == "3":
        folder = prompt_user("Research folder path")
        if folder and os.path.isdir(folder):
            notes = get_notes(folder)
            if notes:
                for i, note in enumerate(notes, 1):
                    console.print(f"\n[bold]Note #{i}[/bold] by {note.get('author', '?')} at {note.get('timestamp', '?')}")
                    console.print(f"  {note.get('text', '')[:200]}")
            else:
                show_info("No notes yet.")

    elif choice == "4":
        folder = prompt_user("Research folder path")
        if folder and os.path.isdir(folder):
            note_text = prompt_user("Your note")
            if note_text:
                add_note(folder, note_text)
                show_success("Note added.")


# ═══════════════════════════════════════════════════════════
#  NEW CLI COMMANDS
# ═══════════════════════════════════════════════════════════

@main.command()
@click.argument("topic_a")
@click.argument("topic_b")
@click.option("-o", "--output", default="report", help="Output type")
@click.option("-p", "--provider", default=None, help="AI provider")
def compare(topic_a, topic_b, output, provider):
    """Compare two topics side-by-side"""
    provider = provider or config.get("default_provider", "sky")
    result = comparative_research(topic_a, topic_b, output_type=output, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Comparison saved → {result['output_file']}")


@main.command()
@click.argument("claims", nargs=-1)
@click.option("-p", "--provider", default=None, help="AI provider")
def factcheck(claims, provider):
    """Fact-check claims against real sources"""
    provider = provider or config.get("default_provider", "sky")
    if not claims:
        show_error("Provide claims to check. Example: kseye factcheck 'claim1' 'claim2'")
        return
    result = fact_check("\n".join(claims), provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Fact-check saved → {result['output_file']}")


@main.command()
@click.argument("topic")
@click.option("-p", "--provider", default=None, help="AI provider")
def timeline(topic, provider):
    """Build chronological timeline"""
    provider = provider or config.get("default_provider", "sky")
    result = build_timeline(topic, provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Timeline saved → {result['output_file']}")


@main.command()
@click.argument("topics", nargs=-1, required=True)
@click.option("-p", "--provider", default=None, help="AI provider")
def batch(topics, provider):
    """Batch research multiple topics"""
    provider = provider or config.get("default_provider", "sky")
    result = batch_research(list(topics), provider=provider)
    if result and result.get("status") == "complete":
        show_success(f"Done: {result['successful']}/{len(topics)} completed")


@main.command()
@click.argument("query", required=False)
def search(query):
    """Search past research history"""
    if not query:
        query = prompt_user("Search query")
    if not query:
        return
    results = search_research_history(query)
    if results:
        rows = [[r.get("topic", "?")[:40], str(r.get("score", 0)), r.get("match", ""), r.get("folder", "")[-40:]] for r in results]
        display_table(["Topic", "Score", "Match", "Folder"], rows)
    else:
        show_info("No results found.")


# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
