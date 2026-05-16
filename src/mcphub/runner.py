"""Runner — executes installed MCP servers."""

from __future__ import annotations

import os
import subprocess
import sys

from rich.console import Console


class Runner:
    """Launches MCP server processes."""

    def __init__(self, console: Console, dry_run: bool = False) -> None:
        self.console = console
        self.dry_run = dry_run

    def run(self, entry: dict) -> None:
        command = entry["command"]
        args = entry.get("args", [])
        env_vars = entry.get("env", {})

        cmd = [command] + args
        self.console.print(f"\n[bold]Starting [cyan]{entry['name']}[/] MCP server...[/]")

        if self.dry_run:
            self.console.print(f"  [dim]Would run:[/] {' '.join(cmd)}")
            if env_vars:
                self.console.print("  [dim]With env:[/]")
                for k, v in env_vars.items():
                    resolved = os.environ.get(k, v)
                    self.console.print(f"    {k}={resolved}")
            return

        resolved_env = {**os.environ}
        for k, v in env_vars.items():
            if k in os.environ:
                resolved_env[k] = os.environ[k]
            elif v.startswith("<") and v.endswith(">"):
                self.console.print(
                    f"[yellow]Warning:[/] {k} is not set — it needs a real value, not {v}"
                )

        try:
            proc = subprocess.Popen(cmd, env=resolved_env)
            self.console.print(f"[green]Running[/] (PID {proc.pid}). Press Ctrl+C to stop.")
            proc.wait()
        except KeyboardInterrupt:
            self.console.print("\n[dim]Shutting down...[/]")
            proc.terminate()
            proc.wait()
        except FileNotFoundError:
            self.console.print(
                f"[red]Command not found:[/] {command}\n"
                f"[dim]Make sure it's installed. Try: mcphub install {entry['name']}[/]"
            )
            raise SystemExit(1)
