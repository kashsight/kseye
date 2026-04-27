"""
ks-eye v2.0 — Clean Console UI
Minimal, Rich-based display utilities.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def banner():
    """Main application banner."""
    return Panel(
        "[bold cyan]ks-eye[/bold cyan] v2.0 — [dim]Online AI Research Platform[/dim]\n"
        "[dim]Scrape real websites → AI reads & analyzes → Structured reports[/dim]",
        border_style="cyan",
    )


def show_success(msg):
    console.print(f"[bold green]✓[/bold green] {msg}")


def show_error(msg):
    console.print(f"[bold red]✗[/bold red] {msg}")


def show_warning(msg):
    console.print(f"[bold yellow]⚠[/bold yellow] {msg}")


def show_info(msg):
    console.print(f"[bold blue]ℹ[/bold blue] {msg}")


def show_section(title):
    console.print(f"\n[bold green]━━━ {title} ━━━[/bold green]")


def show_panel(title, content, border_style="cyan"):
    console.print(Panel(content, title=title, border_style=border_style))


def show_panel_md(title, content, border_style="cyan"):
    """Show a panel with markdown rendering."""
    console.print(Panel(Markdown(content), title=title, border_style=border_style))


def prompt_user(question, default=""):
    """Prompt user for input with optional default."""
    if default:
        return console.input(f"[bold cyan]?[/bold cyan] {question} [dim]({default})[/dim]: ").strip() or default
    return console.input(f"[bold cyan]?[/bold cyan] {question}: ").strip()


def confirm(question, default=True):
    """Ask yes/no question."""
    suffix = "Y/n" if default else "y/N"
    answer = console.input(f"[bold cyan]?[/bold cyan] {question} [{suffix}]: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes", "ye", "1", "true")


def make_progress():
    """Create a progress spinner."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def display_table(headers, rows):
    """Display tabular data."""
    table = Table()
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*[str(c) for c in row])
    console.print(table)
