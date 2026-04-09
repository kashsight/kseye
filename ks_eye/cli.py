"""
ks-eye CLI v3.1 — Offline-First with Optional Online AI
Full offline data processing + quick online research mode
"""

import sys
import os
import json
from collections import Counter
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ks_eye import __version__
from ks_eye.ui import console, show_banner, show_success, show_error, show_warning, show_info, prompt_user
from ks_eye.config import config
from ks_eye.engines.tgpt_engine import check_tgpt_installed
from ks_eye.engines.research_assistant import ResearchAssistant, ResearchSession
from ks_eye.engines.data_processing import (
    DataImport, DataValidator, CrossTabulator, AutoCoder, ASCIICharts, Statistics,
)
from ks_eye.engines.quick_research import quick_online_research, format_quick_report

console = Console()
assistant = ResearchAssistant()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """ks-eye v3.1: Offline-First Research Assistant"""
    if ctx.invoked_subcommand is None:
        interactive_mode()


@main.command()
def version():
    """Show version"""
    has_ai = check_tgpt_installed()
    mode = "[green]Online AI ready[/green]" if has_ai else "[yellow]Offline mode[/yellow]"
    console.print(f"[bold cyan]ks-eye[/bold cyan] v{__version__} — {mode}")


# ═══════════════════════════════════════════════════════════
#  QUICK ONLINE RESEARCH
# ═══════════════════════════════════════════════════════════

@main.command()
@click.argument("query")
@click.option("-o", "--output", type=click.Path(), help="Save to file")
@click.option("-m", "--max-sources", default=30, help="Max sources")
@click.option("-p", "--provider", default="sky", help="AI provider")
def quick(query, output, max_sources, provider):
    """Quick AI-powered online research (scrapes + AI analysis)"""
    show_banner()

    if not check_tgpt_installed():
        show_error("tgpt not installed. Install: go install github.com/aikooo/tgpt/v2@latest")
        sys.exit(1)

    console.print(f"[bold cyan]Quick Research:[/bold cyan] {query}")
    result = quick_online_research(query, max_sources, provider)

    report = format_quick_report(result)
    console.print(report)

    if output:
        with open(output, "w") as f:
            f.write(report)
        show_success(f"Saved to {output}")


# ═══════════════════════════════════════════════════════════
#  DATA PROCESSING — FULLY OFFLINE
# ═══════════════════════════════════════════════════════════

@main.command()
@click.argument("file_path")
def validate(file_path):
    """Validate data file (CSV/JSON) — fully offline"""
    show_banner()
    if not os.path.exists(file_path):
        show_error(f"File not found: {file_path}"); return

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        result = DataImport.from_csv_file(file_path)
    elif ext == ".json":
        with open(file_path) as f:
            result = DataImport.from_json_string(f.read())
    else:
        show_error("Supported: .csv, .json"); return

    if result.get("status") != "ok":
        show_error(result.get("message", "Import failed")); return

    data = result["data"]
    validator = DataValidator(data, result["columns"])
    report = validator.run_all_checks()

    console.print(Panel(
        f"[bold]Rows:[/bold] {report['row_count']}  "
        f"[bold]Columns:[/bold] {report['column_count']}\n"
        f"[bold]Quality Score:[/bold] {report['quality_score']}/100 ({report['rating']})\n\n"
        f"[red]Issues:[/red] {len(report['issues'])}\n"
        f"[yellow]Warnings:[/yellow] {len(report['warnings'])}\n"
        f"[dim]Info:[/dim] {len(report['info'])}",
        title="📊 Data Validation Report",
        border_style="cyan" if report["quality_score"] >= 70 else "yellow",
    ))

    for issue in report["issues"]:
        console.print(f"  [red]✗ {issue}[/red]")
    for warn in report["warnings"]:
        console.print(f"  [yellow]⚠ {warn}[/yellow]")
    for info in report["info"]:
        console.print(f"  [dim]ℹ {info}[/dim]")


@main.command()
@click.argument("file_path")
@click.option("--chart", "-c", multiple=True, help="Column to chart (repeat for multiple)")
@click.option("--cross", "-x", nargs=2, multiple=True, help="Cross-tab: row_col col_col")
@click.option("--code", multiple=True, help="Column to auto-code (open-ended)")
@click.option("--ai-code", is_flag=True, help="Use AI for auto-coding")
def analyze(file_path, chart, cross, code, ai_code):
    """Analyze data file — charts, cross-tabs, auto-coding (offline)"""
    show_banner()
    if not os.path.exists(file_path):
        show_error(f"File not found: {file_path}"); return

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        result = DataImport.from_csv_file(file_path)
    elif ext == ".json":
        with open(file_path) as f:
            result = DataImport.from_json_string(f.read())
    else:
        show_error("Supported: .csv, .json"); return

    if result.get("status") != "ok":
        show_error(result.get("message", "Import failed")); return

    data = result["data"]
    columns = result["columns"]

    # Show data overview
    console.print(Panel(
        f"[bold]Rows:[/bold] {result['row_count']}  [bold]Columns:[/bold] {len(columns)}\n"
        f"[bold]Columns:[/bold] {', '.join(columns[:15])}{'...' if len(columns) > 15 else ''}",
        title="📁 Data Overview",
        border_style="cyan",
    ))

    # Charts
    for col in chart:
        if col not in columns:
            show_warning(f"Column not found: {col}"); continue
        freq = Counter(str(row.get(col, "")) for row in data)
        console.print(ASCIICharts.frequency_table(freq, title=f"Distribution: {col}"))

    # Cross-tabulation
    for row_col, col_col in cross:
        ct = CrossTabulator(data).cross_tab(row_col, col_col)
        console.print(Panel(
            f"[bold]Cross-Tab:[/bold] {row_col} × {col_col}\n"
            f"[bold]Chi-Square:[/bold] {ct['chi_square']}\n"
            f"[bold]Categories:[/bold] {ct['row_categories']} × {ct['col_categories']}",
            title="📊 Cross-Tabulation",
            border_style="green",
        ))
        # Print table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column(row_col, style="cyan")
        for c in ct["col_totals"]:
            table.add_column(c[:15], style="green")
        table.add_column("Total", style="yellow")
        for r, vals in ct["counts"].items():
            row = [r[:20]]
            total = 0
            for c in ct["col_totals"]:
                v = vals.get(c, 0)
                row.append(str(v))
                total += v
            row.append(str(total))
            table.add_row(*row)
        console.print(table)
        console.print()

    # Auto-coding
    for col in code:
        if col not in columns:
            show_warning(f"Column not found: {col}"); continue
        responses = [str(row.get(col, "")) for row in data]
        coder = AutoCoder()
        coding_result = coder.code_responses(responses, col, use_ai=ai_code)
        if coding_result.get("status") == "ok":
            console.print(Panel(
                f"[bold]Method:[/bold] {coding_result['method']}\n"
                f"[bold]Responses coded:[/bold] {coding_result['total_responses']}\n"
                f"[bold]Themes found:[/bold] {coding_result['code_count']}",
                title="🏷️ Auto-Coding Results",
                border_style="green",
            ))
            for theme, info in coding_result["codebook"].items():
                console.print(f"  [cyan]{theme}[/cyan]: {info['count']} ({info['percentage']:.1f}%)")
                for ex in info["examples"][:2]:
                    console.print(f"    [dim]→ {ex[:100]}[/dim]")
            console.print()

    # Numeric stats
    for col in columns:
        values = [row.get(col, "") for row in data]
        nums = []
        for v in values:
            try:
                nums.append(float(v))
            except (ValueError, TypeError):
                pass
        if len(nums) > 3:
            stats = Statistics.describe(nums)
            console.print(Panel(
                f"Mean: {stats['mean']}  Median: {stats['median']}  "
                f"Std: {stats['std_dev']}  Range: {stats['range']}\n"
                f"Min: {stats['min']}  Max: {stats['max']}  "
                f"Q1: {stats['q1']}  Q3: {stats['q3']}",
                title=f"📈 Statistics: {col}",
                border_style="magenta",
            ))


# ═══════════════════════════════════════════════════════════
#  INTERACTIVE MODE
# ═══════════════════════════════════════════════════════════

def interactive_mode():
    show_banner()

    has_ai = check_tgpt_installed()
    mode_tag = "[green]AI Online[/green]" if has_ai else "[yellow]Offline Only[/yellow]"
    console.print(f"Mode: {mode_tag}")
    console.print()

    # Show existing sessions
    saved = ResearchSession.list_sessions()
    if saved:
        lines = []
        for i, s in enumerate(saved[-5:], 1):
            tag = " [green]✓[/green]" if s["has_report"] else ""
            lines.append(f"  [cyan]{i}[/cyan]. [{s['step']}] {s['topic'][:45]} ({s['created'][:10]}){tag}")
        console.print(Panel(
            "[bold yellow]Research Folders:[/bold yellow]\n" + "\n".join(lines),
            title=" Resume?",
            border_style="yellow",
        ))
        resume = prompt_user("Resume (number) or n", "n")
        if resume.strip().lower() != "n":
            try:
                idx = int(resume.strip()) - 1
                if 0 <= idx < len(saved):
                    assistant.session.load_session(saved[idx]["folder"])
                    show_success(f"Loaded: {saved[idx]['topic']}")
                    _resume_from_current_step()
                    return
            except (ValueError, IndexError):
                pass

    console.print()
    console.print(Panel(
        "[bold cyan]1[/bold cyan].   New Research (step-by-step, offline-first)\n"
        "[bold cyan]2[/bold cyan].   Quick Online Research (AI scrapes everything)\n"
        "[bold cyan]3[/bold cyan].   Analyze Data File (CSV/JSON, offline)\n"
        "[bold cyan]4[/bold cyan].   Validate Data File (offline)\n"
        "[bold cyan]5[/bold cyan].   Settings\n"
        "[bold red]0[/bold red].   Exit",
        title=" ks-eye v3.1 Main Menu",
        border_style="cyan",
    ))

    choice = prompt_user("Select", "1")

    if choice == "1":
        console.print()
        console.print("[bold cyan]Starting step-by-step research...[/bold cyan]")
        console.print("[dim]Everything saved as .txt in auto-created folder[/dim]")
        console.print()
        _run_workflow()
    elif choice == "2":
        if not has_ai:
            show_error("tgpt not installed. Install: go install github.com/aikooo/tgpt/v2@latest")
            return
        query = prompt_user("Research query")
        if query:
            console.print(f"\n[cyan]Quick research: {query}[/cyan]\n")
            result = quick_online_research(query)
            report = format_quick_report(result)
            console.print(report)
            save = prompt_user("Save report? (y/n)", "y")
            if save.lower() == "y":
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe = "".join(c if c.isalnum() else "_" for c in query)[:30]
                path = os.path.join(config.RESEARCH_DIR, f"quick_{safe}_{ts}.txt")
                with open(path, "w") as f:
                    f.write(report)
                show_success(f"Saved to {path}")
    elif choice == "3":
        fpath = prompt_user("Data file path (.csv or .json)")
        if fpath and os.path.exists(fpath):
            console.print(f"\n[cyan]Analyzing: {fpath}[/cyan]\n")
            # Run analyze command logic inline
            _analyze_file_interactive(fpath)
        else:
            show_error("File not found")
    elif choice == "4":
        fpath = prompt_user("Data file path (.csv or .json)")
        if fpath and os.path.exists(fpath):
            _validate_file_interactive(fpath)
        else:
            show_error("File not found")
    elif choice == "5":
        _show_settings()
    elif choice == "0":
        console.print("[bold green]Thanks for using ks-eye![/bold green]")


def _analyze_file_interactive(fpath):
    """Interactive data analysis"""
    ext = os.path.splitext(fpath)[1].lower()
    if ext == ".csv":
        result = DataImport.from_csv_file(fpath)
    elif ext == ".json":
        with open(fpath) as f:
            result = DataImport.from_json_string(f.read())
    else:
        show_error("Supported: .csv, .json"); return

    if result.get("status") != "ok":
        show_error(result.get("message", "Import failed")); return

    data = result["data"]
    columns = result["columns"]

    console.print(Panel(
        f"[bold]Rows:[/bold] {result['row_count']}  [bold]Columns:[/bold] {len(columns)}\n"
        f"[bold]Columns:[/bold] {', '.join(columns[:15])}",
        title="📁 Data Loaded",
        border_style="cyan",
    ))

    # Validation
    validator = DataValidator(data, columns)
    report = validator.run_all_checks()
    console.print(f"[bold]Quality:[/bold] {report['quality_score']}/100 ({report['rating']})")
    if report["issues"]:
        for i in report["issues"]:
            console.print(f"  [red]✗ {i}[/red]")

    # Show frequency charts for categorical columns
    console.print()
    console.print("[bold cyan]Column Distributions:[/bold cyan]")
    for col in columns[:10]:
        freq = Counter(str(row.get(col, "")) for row in data)
        if len(freq) <= 15 and len(freq) > 1:
            console.print(ASCIICharts.frequency_table(freq, title=col))

    # Ask for cross-tabs
    console.print()
    ct_choice = prompt_user("Cross-tabulate? Enter: col1 col2 (or n)", "n")
    if ct_choice.lower() != "n":
        parts = ct_choice.split()
        if len(parts) >= 2:
            ct = CrossTabulator(data).cross_tab(parts[0], parts[1])
            console.print(Panel(f"Chi-Square: {ct['chi_square']}", title="Cross-Tab"))

    # Ask for auto-coding
    console.print()
    code_choice = prompt_user("Auto-code open-ended? Enter column name (or n)", "n")
    if code_choice.lower() != "n" and code_choice in columns:
        responses = [str(row.get(code_choice, "")) for row in data]
        has_ai = check_tgpt_installed()
        coder = AutoCoder()
        cr = coder.code_responses(responses, code_choice, use_ai=has_ai)
        if cr.get("status") == "ok":
            console.print(f"[bold]Themes:[/bold] {cr['code_count']}")
            for theme, info in cr["codebook"].items():
                console.print(f"  [cyan]{theme}[/cyan]: {info['count']} ({info['percentage']:.1f}%)")


def _validate_file_interactive(fpath):
    ext = os.path.splitext(fpath)[1].lower()
    if ext == ".csv":
        result = DataImport.from_csv_file(fpath)
    elif ext == ".json":
        with open(fpath) as f:
            result = DataImport.from_json_string(f.read())
    else:
        show_error("Supported: .csv, .json"); return
    if result.get("status") != "ok":
        show_error(result.get("message")); return
    validator = DataValidator(result["data"], result["columns"])
    report = validator.run_all_checks()
    console.print(Panel(
        f"Quality: {report['quality_score']}/100 ({report['rating']})\n"
        f"Issues: {len(report['issues'])}  Warnings: {len(report['warnings'])}",
        title="Validation",
        border_style="cyan" if report["quality_score"] >= 70 else "yellow",
    ))


def _show_settings():
    s = config.get_all()
    table = Table(title="Settings", border_style="cyan", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    for k, v in s.items():
        if isinstance(v, (list, dict)):
            v = str(v)[:40]
        table.add_row(k, str(v))
    console.print(table)


def _resume_from_current_step():
    step = assistant.session.state.get("step", "topic_definition")
    show_info(f"Resuming from: {step.replace('_', ' ').title()}")
    console.print()

    step_map = {
        "topic_definition": _run_workflow,
        "proposal_generation": lambda: _continue_to_questionnaire(),
        "questionnaire_design": lambda: _continue_to_questionnaire(),
        "data_collection": lambda: _continue_to_data_collection(),
        "data_analysis": lambda: _continue_to_analysis(),
        "literature_review": lambda: _continue_to_lit_review(),
        "report_writing": lambda: _continue_to_report(),
        "final_output": _compile_and_save,
        "complete": lambda: show_success("Session already complete!"),
    }
    handler = step_map.get(step)
    if handler:
        handler()


# ── Workflow helpers imported from research_assistant flow ──
def _run_workflow():
    """Full step-by-step workflow"""
    # Step 1: Topic
    _print_step_header(1, "Topic Definition")
    result = assistant.step_topic()
    console.print(Panel(result.get("prompt", ""), title="📝 Define Your Topic", border_style="cyan"))
    topic_input = _multiline_input("Enter topic details (empty line to finish)")
    result = assistant.step_topic(topic_input)
    if result.get("status") == "error":
        show_error(result["message"]); return
    show_success(result.get("message", ""))

    # Step 2: Proposal
    _print_step_header(2, "Proposal")
    if check_tgpt_installed():
        result = assistant.step_proposal("draft")
        if result.get("status") == "error":
            show_error(result["message"]); return
        if result.get("status") == "manual_entry":
            _handle_manual_proposal(); return
        _show_panel("Proposal Draft", result.get("proposal", "")[:1500])
        while True:
            action = prompt_user("approve / edit / regenerate", "approve")
            if action == "approve":
                result = assistant.step_proposal("approve")
                if result.get("status") == "approved":
                    show_success(result.get("message", "")); break
            elif action.startswith("edit"):
                edits = prompt_user("Describe edits")
                result = assistant.step_proposal("edit", edits)
                if result.get("status") == "revised":
                    _show_panel("Revised", result.get("proposal", "")[:1500])
            elif action == "regenerate":
                result = assistant.step_proposal("regenerate")
                if result.get("proposal"):
                    _show_panel("New Draft", result.get("proposal", "")[:1500])
    else:
        _handle_manual_proposal()

    # Step 3-8: Continue
    _continue_to_questionnaire()


def _handle_manual_proposal():
    console.print(Panel(
        "AI unavailable. Type your proposal or 'skip'.",
        title="Manual Entry", border_style="yellow"
    ))
    action = prompt_user("Enter proposal text or 'skip'", "skip")
    if action.strip().lower() != "skip":
        assistant.session.state["proposal"] = {"text": action, "status": "approved"}
    else:
        assistant.session.state["proposal"] = {"text": "No proposal drafted.", "status": "approved"}
    assistant.session.state["step"] = "questionnaire_design"
    assistant.session._save_state()
    _continue_to_questionnaire()


def _continue_to_questionnaire():
    _print_step_header(3, "Questionnaire")
    if check_tgpt_installed():
        result = assistant.step_questionnaire("draft")
        if result.get("status") == "error":
            show_error(result["message"]); return
        _show_panel("Questionnaire JSON", result.get("questionnaire_json", "")[:1500])
        while True:
            action = prompt_user("approve / edit / regenerate", "approve")
            if action == "approve":
                result = assistant.step_questionnaire("approve")
                if result.get("status") == "approved":
                    show_success(result.get("message", "")); break
            elif action.startswith("edit"):
                edits = prompt_user("Describe changes")
                result = assistant.step_questionnaire("edit", edits)
                if result.get("status") == "revised":
                    _show_panel("Revised", result.get("questionnaire_json", "")[:1500])
            elif action == "regenerate":
                result = assistant.step_questionnaire("regenerate")
                if result.get("questionnaire_json"):
                    _show_panel("New", result.get("questionnaire_json", "")[:1500])
    else:
        action = prompt_user("Enter questionnaire JSON or 'skip'", "skip")
        if action.strip().lower() != "skip":
            try:
                parsed = json.loads(action)
                assistant.session.save_questionnaire(parsed)
            except: show_error("Invalid JSON")
    _continue_to_data_collection()


def _continue_to_data_collection():
    _print_step_header(4, "Data Collection")
    console.print(Panel(
        "Collect data offline. Paste JSON or CSV when ready, or 'skip'.",
        title="📊 Offline Collection", border_style="yellow"
    ))
    data_input = prompt_user("Paste data or 'skip'", "skip")
    if data_input.strip().lower() != "skip":
        # Try CSV or JSON
        if data_input.strip().startswith("{") or data_input.strip().startswith("["):
            result = assistant.step_data_collection("receive", data_input)
        elif os.path.exists(data_input.strip()):
            # It's a file path
            ext = os.path.splitext(data_input.strip())[1].lower()
            if ext == ".csv":
                imp = DataImport.from_csv_file(data_input.strip())
            elif ext == ".json":
                with open(data_input.strip()) as f:
                    imp = DataImport.from_json_string(f.read())
            else:
                imp = {"status": "error", "message": "Unsupported format"}
            if imp.get("status") == "ok":
                assistant.session.save_collected_data(imp["data"])
                assistant.session.state["response_count"] = imp["row_count"]
                assistant.session.state["step"] = "data_analysis"
                assistant.session._save_state()
                show_success(f"Loaded {imp['row_count']} responses from {data_input.strip()}")
                result = {"status": "received"}
            else:
                show_error(imp.get("message", "Import failed")); result = {"status": "error"}
        else:
            # Try as CSV string
            imp = DataImport.from_csv_string(data_input)
            if imp.get("status") == "ok":
                assistant.session.save_collected_data(imp["data"])
                assistant.session.state["response_count"] = imp["row_count"]
                assistant.session.state["step"] = "data_analysis"
                assistant.session._save_state()
                show_success(f"Loaded {imp['row_count']} responses from CSV")
                result = {"status": "received"}
            else:
                show_error("Could not parse as CSV or JSON"); result = {"status": "error"}
    else:
        result = {"status": "skipped"}

    if assistant.session.state.get("collected_data"):
        _continue_to_analysis()
    else:
        _continue_to_lit_review()


def _continue_to_analysis():
    _print_step_header(5, "Data Analysis")
    data = assistant.session.state.get("collected_data", [])
    if not data:
        show_info("No data to analyze"); _continue_to_lit_review(); return

    # Validate
    cols = data[0].keys() if data else []
    validator = DataValidator(data, cols)
    vreport = validator.run_all_checks()
    console.print(f"[bold]Quality:[/bold] {vreport['quality_score']}/100 ({vreport['rating']})")

    # Frequency charts
    console.print()
    console.print("[bold cyan]Distributions:[/bold cyan]")
    for col in list(cols)[:8]:
        freq = Counter(str(row.get(col, "")) for row in data)
        if len(freq) <= 15 and len(freq) > 1:
            console.print(ASCIICharts.frequency_table(freq, title=col))

    # Cross-tabs
    console.print()
    ct_choice = prompt_user("Cross-tab? Enter: col1 col2 (or n)", "n")
    if ct_choice.lower() != "n":
        parts = ct_choice.split()
        if len(parts) >= 2:
            ct = CrossTabulator(data).cross_tab(parts[0], parts[1])
            console.print(Panel(f"Chi-Square: {ct['chi_square']}", title="Cross-Tab"))

    # AI analysis
    if check_tgpt_installed():
        console.print("\n[cyan]Running AI analysis...[/cyan]")
        result = assistant.step_data_analysis("analyze")
        if result.get("analysis"):
            _show_panel("AI Analysis", result.get("analysis", "")[:1500])
            action = prompt_user("approve / reanalyze", "approve")
            if action.startswith("reanalyze"):
                d = prompt_user("Focus on?")
                result = assistant.step_data_analysis("reanalyze", d)
    else:
        show_info("AI analysis unavailable. Using offline statistics only.")
        assistant.session.state["analysis_results"] = {"text": "Offline analysis only.", "status": "approved"}

    _continue_to_lit_review()


def _continue_to_lit_review():
    _print_step_header(6, "Literature Review")
    if not check_tgpt_installed():
        show_info("AI unavailable. Skipping literature review.")
        assistant.session.state["literature_review"] = "No literature review (AI unavailable)."
        _continue_to_report(); return

    do_lit = prompt_user("Include literature review? (y/n)", "y")
    if do_lit.lower() == "y":
        result = assistant.step_literature_review("search")
        if result.get("sources"):
            console.print(Panel(
                f"Found {result.get('total_sources', 0)} sources\n" +
                "\n".join(f"  [{i+1}] {s.get('title', '')[:60]}" for i, s in enumerate(result.get("sources", [])[:10])),
                title="📚 Sources", border_style="cyan"
            ))
            sel = prompt_user("Select (1,2,3 or 'all')", "all")
            result = assistant.step_literature_review("select", sel)
            if result.get("literature_review"):
                _show_panel("Literature Review", result.get("literature_review", "")[:1500])
    _continue_to_report()


def _continue_to_report():
    _print_step_header(7, "Report")
    if not check_tgpt_installed():
        show_info("AI unavailable. Compiling from available content.")
        assistant.session.state["report_sections"]["findings"] = {
            "text": "Findings from offline analysis.", "status": "approved"
        }
        assistant.session.state["report_sections"]["conclusion"] = {
            "text": "Conclusion based on available data.", "status": "approved"
        }
        _compile_and_save(); return

    sections = ["executive_summary", "introduction", "methodology", "findings", "discussion", "recommendations", "conclusion"]
    for sec in sections:
        console.print(f"\n[cyan]Drafting: {sec.replace('_', ' ').title()}...[/cyan]")
        result = assistant.step_report_writing(sec, "draft")
        if result.get("status") == "drafted":
            assistant.session.save_report_section(sec, result.get("content", ""))
            assistant.session.state["report_sections"][sec] = {"content": result["content"], "status": "approved"}
            assistant.session._save_state()
            show_success(f"{sec.replace('_', ' ').title()} saved")

    _compile_and_save()


def _compile_and_save():
    _print_step_header(8, "Final Report")
    sections = {k: v for k, v in assistant.session.state.get("report_sections", {}).items() if v.get("status") == "approved" or v.get("content")}
    if not sections:
        show_error("No sections to compile"); return

    lines = ["=" * 80, assistant.session.state.get("topic", "Research Report").upper().center(80), "=" * 80, ""]
    for sec_key in ["executive_summary", "introduction", "literature_review", "methodology", "findings", "discussion", "recommendations", "conclusion"]:
        if sec_key in sections:
            content = sections[sec_key].get("content", sections[sec_key].get("text", ""))
            if content:
                lines.append(sec_key.replace("_", " ").upper())
                lines.append("=" * 80)
                lines.append(content)
                lines.append("")
                lines.append("-" * 80)
                lines.append("")

    lines.extend(["=" * 80, f"End of Report — ks-eye v{__version__}", "=" * 80])
    report = "\n".join(lines)
    assistant.session.save_final_report(report)
    show_success(f"Report saved to {assistant.session.folder}/report.txt")

    console.print(Panel(
        f"[bold green]Complete![/bold green]\nFolder: {assistant.session.folder}\n"
        f"All files saved as .txt in session folder.",
        title="✅ Done", border_style="green"
    ))


# ── Display Helpers ──
def _print_step_header(step_num, title):
    console.print()
    console.print(Panel(f"[bold cyan]Step {step_num}[/bold cyan]: {title}", border_style="cyan"))
    console.print()

def _multiline_input(prompt_text):
    console.print(f"[dim]{prompt_text}[/dim]")
    console.print("[dim](Enter on empty line to finish)[/dim]")
    lines = []
    while True:
        line = console.input("[bold green]  ► [/bold green]")
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines)

def _show_panel(title, text):
    if text:
        console.print(Panel(f"[dim]{text}[/dim]", title=title, border_style="cyan"))

def _show_section(title, text):
    console.print(Panel(f"[dim]{text[:1200]}{'...' if len(text) > 1200 else ''}[/dim]", title=f"📝 {title}", border_style="blue"))


if __name__ == "__main__":
    main()
