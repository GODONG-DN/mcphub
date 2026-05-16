"""Profile manager — save and restore sets of MCP server configurations."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from mcphub.config import CACHE_DIR, ConfigManager

PROFILE_DIR = CACHE_DIR / "profiles"


class ProfileManager:
    """Snapshot current AI client MCP configs so you can switch between setups."""

    def __init__(self, console: Console) -> None:
        self.console = console

    def save(self, name: str) -> None:
        mgr = ConfigManager(console=self.console)
        servers = mgr.list_servers()

        if not any(servers.values()):
            self.console.print("[yellow]No configured servers to save.[/]")
            return

        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        path = PROFILE_DIR / f"{name}.json"

        snapshot: dict = {}
        for client_id, client_servers in servers.items():
            if client_servers:
                snapshot[client_id] = client_servers

        with open(path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        total = sum(len(v) for v in snapshot.values())
        self.console.print(f"[green]Saved[/] profile [bold]{name}[/] ({total} servers)")

    def load(self, name: str) -> None:
        path = PROFILE_DIR / f"{name}.json"
        if not path.exists():
            self.console.print(f"[red]Profile not found:[/] {name}")
            return

        with open(path, encoding="utf-8") as f:
            snapshot = json.load(f)

        mgr = ConfigManager(console=self.console)
        for client_id, servers in snapshot.items():
            for server_name, entry in servers.items():
                mgr.add_server(
                    name=server_name,
                    command=entry.get("command", ""),
                    args=entry.get("args", []),
                    env=entry.get("env", {}),
                )

        total = sum(len(v) for v in snapshot.values())
        self.console.print(f"[green]Loaded[/] profile [bold]{name}[/] ({total} servers)")

    def list_all(self) -> None:
        if not PROFILE_DIR.exists():
            self.console.print("[yellow]No saved profiles.[/]")
            return

        profiles = sorted(PROFILE_DIR.glob("*.json"))
        if not profiles:
            self.console.print("[yellow]No saved profiles.[/]")
            return

        table = Table(title=None, show_header=True, header_style="bold")
        table.add_column("Profile", style="cyan")
        table.add_column("Servers")

        for p in profiles:
            with open(p, encoding="utf-8") as f:
                snapshot = json.load(f)
            total = sum(len(v) for v in snapshot.values())
            table.add_row(p.stem, str(total))

        self.console.print()
        self.console.print(table)

    def delete(self, name: str) -> None:
        path = PROFILE_DIR / f"{name}.json"
        if not path.exists():
            self.console.print(f"[red]Profile not found:[/] {name}")
            return

        path.unlink()
        self.console.print(f"[green]Deleted[/] profile [bold]{name}[/]")
