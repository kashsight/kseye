"""
ks-eye UI — v3: Human-in-the-Loop Research Assistant
Clean, step-by-step display components
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

BANNER = Text.assemble(
    ("  _  __                       ", "cyan"),
    (" | |/ /___ _   _  ___  ___   ", "bright_cyan"),
    (" _  __           ", "cyan"),
    ("\n", ""),
    (" | ' // _ \\ | | |/ _ \\/ __|  ", "bright_cyan"),
    (" | |/ /___ _   _  ", "cyan"),
    ("\n", ""),
    (" | . \\  __/ |_| |  __/\\__ \\  ", "bright_cyan"),
    (" | ' // _ \\ | | | ", "cyan"),
    ("\n", ""),
    (" |_|\\_\\___|\\__, |\\___||___/  ", "bright_cyan"),
    (" | . \\  __/ |_| | ", "cyan"),
    ("\n", ""),
    ("           |___/             ", "bright_cyan"),
    (" |_|\\_\\___|\\__, | ", "cyan"),
    ("\n", ""),
    ("            ", "bright_cyan"),
    ("           |___/  ", "cyan"),
    (" v3", "yellow"),
)


def show_banner():
    console.print()
    console.print(BANNER)
    console.print()
    console.print(
        Panel(
            "[bold cyan]AI-Human Collaborative Research Assistant[/bold cyan]\n"
            "[dim]AI suggests. You decide. Nothing is fully automated.[/dim]",
            style="cyan",
            border_style="bright_cyan",
        )
    )
    console.print()


def show_success(msg):
    console.print(f"[bold green]✓ {msg}[/bold green]")


def show_error(msg):
    console.print(f"[bold red]✗ {msg}[/bold red]")


def show_warning(msg):
    console.print(f"[bold yellow]⚠ {msg}[/bold yellow]")


def show_info(msg):
    console.print(f"[bold cyan]ℹ {msg}[/bold cyan]")


def prompt_user(text, default=None):
    if default:
        r = console.input(f"[bold green]  ► {text}[/bold green] [dim]({default})[/dim]: ")
        return r if r.strip() else default
    return console.input(f"[bold green]  ► {text}[/bold green]: ")


def display_table_data(title, headers, rows):
    table = Table(title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan", show_header=True, header_style="bold magenta")
    for h in headers:
        table.add_column(h, style="cyan")
    for row in rows:
        table.add_row(*[str(c) for c in row])
    console.print(table)
    console.print()
