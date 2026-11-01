"""Centralized TUI display using Rich for beautiful terminal output."""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.style import Style
from rich import box

console = Console()

# Color palette
_TURQUOISE = "#66e4cbee"
_GREEN = "#95f1a7"
_BLUE = "#3498db"
_YELLOW = "#f1c40f"
_ORANGE = "#e67e22"
_RED = "#fcc5bf"
_LIGHT_RED = "#f7a1a1"
_SILVER = "#bdc3c7"
_CLOUD = "#ecf0f1"
_CORAL = "#faeeb7"
_SKY = "#87ceeb"

# Agent color themes
AGENT_THEMES = {
    "customer_support": {"color": _CLOUD, "icon": "\u2692", "label": "Support"},
    "banking_services": {"color": _CLOUD, "icon": "\u2696", "label": "Banking"},
    "transactions": {"color": _CLOUD, "icon": "\u2690", "label": "Transactions"},
}

# Track last speaker to draw boundaries between turns
_last_role: str | None = None


def _agent_style(agent_name: str) -> dict:
    return AGENT_THEMES.get(agent_name, {"color": "white", "icon": "\u25cf", "label": agent_name.title()})


def show_banner():
    """Display the application banner on startup."""
    banner_text = Text()
    banner_text.append("  Multi-Agent Voice System  ", style=Style(bold=True, color=_CLOUD))

    grid = Table.grid(padding=(0, 0))
    grid.add_row(banner_text)
    grid.add_row(Text("  Powered by Amazon Nova 2 Sonic", style=Style(color=_SILVER)))
    grid.add_row("")
    agents_line = Text()
    agents_line.append("  Available Agents:  ", style=Style(bold=True, color=_SILVER))
    for t in AGENT_THEMES.values():
        agents_line.append(f" {t['icon']} {t['label']} ", style=Style(bold=True, color=t["color"]))
    grid.add_row(agents_line)

    console.print(Panel(
        grid,
        border_style=Style(color=_BLUE),
        box=box.DOUBLE_EDGE,
        padding=(0, 1),
    ))


def show_agent_start(agent_name: str):
    """Show which agent is starting."""
    global _last_role
    _last_role = None
    theme = _agent_style(agent_name)
    console.print()
    console.print(Panel(
        Text(f"{theme['icon']}  Starting conversation with {theme['label']} agent",
             style=Style(bold=True, color=theme["color"]),
             justify="center"),
        border_style=Style(color=theme["color"]),
        box=box.ROUNDED,
        padding=(0, 1),
    ))


def show_streaming_started():
    """Indicate microphone streaming is active."""
    console.print(
        Text("  \u25cf  Listening \u2014 speak into your microphone",
             style=Style(color=_SILVER))
    )


def show_agent_switch(old_agent: str, new_agent: str):
    """Display agent transition as a single banner."""
    old_theme = _agent_style(old_agent)
    new_theme = _agent_style(new_agent)

    transfer_line = Text()
    transfer_line.append(f"{old_theme['icon']} {old_theme['label']}",
                         style=Style(color=old_theme["color"]))
    transfer_line.append("  \u2500\u2500\u25b6  ", style=Style(color=_SILVER))
    transfer_line.append(f"{new_theme['icon']} {new_theme['label']}",
                         style=Style(bold=True, color=new_theme["color"]))

    grid = Table.grid(padding=(0, 0))
    grid.add_column(justify="center")
    grid.add_row(transfer_line)
    grid.add_row(Text(f"Transferring to {new_theme['label']}...",
                      style=Style(color=_SILVER, italic=True)))

    console.print()
    console.print(Panel(
        grid,
        title=f"[bold {_YELLOW}]Agent Transfer[/bold {_YELLOW}]",
        border_style=Style(color=_YELLOW),
        box=box.ROUNDED,
        padding=(0, 2),
        expand=False,
    ))


def show_switch_detected():
    """Show that an agent switch was detected in the stream."""
    console.print(Text("  \u2500\u2500 Agent switch detected \u2500\u2500", style=Style(color=_SILVER)))


def show_tool_use(tool_name: str):
    """Display tool invocation."""
    global _last_role
    _last_role = None
    console.print(Panel(
        Text(f"\u26a1  {tool_name}", style=Style(bold=True, color=_YELLOW)),
        title=f"[bold {_YELLOW}]Tool[/bold {_YELLOW}]",
        title_align="left",
        border_style=Style(color=_YELLOW, dim=True),
        box=box.HEAVY,
        padding=(0, 1),
        expand=False,
    ))


def show_text_output(role: str, content: str):
    """Display conversation text output in bordered panels."""
    global _last_role
    normalized = role.upper()

    if _last_role is not None and _last_role != normalized:
        console.print()

    _last_role = normalized

    if normalized == "USER":
        console.print(Panel(
            Text(content, style=Style(color=_CLOUD)),
            title=Text(" User ", style=Style(bold=True, color="#ffff00")),
            title_align="left",
            border_style=Style(color=_CLOUD, dim=True),
            box=box.ROUNDED,
            padding=(0, 1),
        ))
    else:
        console.print(Panel(
            Text(content, style=Style(color=_CLOUD)),
            title=Text(" Agent ", style=Style(bold=True, color="#00ff41")),
            title_align="left",
            border_style=Style(color=_CLOUD, dim=True),
            box=box.ROUNDED,
            padding=(0, 1),
        ))


def show_history_loaded(count: int):
    """Show conversation history was loaded."""
    console.print(Text(f"  \u21bb Loaded {count} messages from history", style=Style(color=_SILVER)))


def show_music_playing():
    """Indicate transition music is playing."""
    console.print(Text("  \u266b Playing transition music...", style=Style(color=_SILVER, italic=True)))


def show_music_stopped():
    """Indicate transition music stopped."""
    pass  # silent


def show_conversation_ended():
    """Display conversation ended message."""
    console.print()
    console.print(Panel(
        Text("Session ended. Goodbye!", style=Style(bold=True, color=_SILVER), justify="center"),
        border_style=Style(color=_SILVER),
        box=box.ROUNDED,
        padding=(0, 1),
        expand=False,
    ))


def show_interrupted():
    """Display user interruption message."""
    console.print()
    console.print(Text("Interrupted by user", style=Style(color=_SILVER)))


def show_error(message: str):
    """Display an error message."""
    console.print(Text(f"  Error: {message}", style=Style(bold=True, color=_RED)))


def show_goodbye():
    """Display goodbye on exit."""
    console.print()
    console.print(Text("Goodbye!", style=Style(bold=True, color=_SILVER)))
