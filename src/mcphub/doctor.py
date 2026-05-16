"""Environment doctor — checks your system for MCP server prerequisites."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mcphub.config import _CLIENTS


_TESTS = [
    ("Node.js / npm", ["npm", "npx"]),
    ("Deno (optional)", ["deno"]),
    ("Python 3", ["python3", "python"]),
    ("pip", ["pip3", "pip"]),
    ("uv (recommended)", ["uv", "uvx"]),
    ("git", ["git"]),
    ("docker (optional)", ["docker"]),
]


def run_check(console: Console) -> None:
    """Run a full environment health check and print the report."""

    console.print()
    console.print(Panel("[bold]mcphub doctor[/] — checking your environment...", border_style="cyan"))

    # --- Tools ---
    table = Table(title="CLI Tools", header_style="bold")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Path")

    for label, candidates in _TESTS:
        found = None
        for c in candidates:
            p = shutil.which(c)
            if p:
                found = p
                break

        if found:
            # Mark uv as "recommended"
            status = (
                "[green]found[/] [dim](recommended)[/]"
                if label.startswith("uv")
                else "[green]found[/]"
            )
            table.add_row(label, status, str(found))
        else:
            if "(optional)" in label.lower() or "(recommended)" in label.lower():
                table.add_row(label, "[dim]not found (optional)[/]", "-")
            else:
                table.add_row(label, "[red]missing[/]", "-")

    console.print(table)

    # --- AI Clients ---
    client_table = Table(title="AI Clients", header_style="bold")
    client_table.add_column("Client")
    client_table.add_column("Config")

    for client_id, info in _CLIENTS.items():
        path = info["resolver"]()
        status = str(path) if path else "[dim]not found[/]"
        client_table.add_row(info["name"], status)

    console.print(client_table)

    # --- Python ---
    console.print(f"\n  [bold]Python[/]: {sys.version}")
    console.print(f"  [bold]Platform[/]: {sys.platform}")

    console.print()
