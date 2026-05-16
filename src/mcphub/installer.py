"""Installer — handles fetching and setting up MCP servers."""

from __future__ import annotations

import shutil
import subprocess

from rich.console import Console


class Installer:
    """Pulls down MCP servers and gets them ready to run."""

    def __init__(self, console: Console, dry_run: bool = False) -> None:
        self.console = console
        self.dry_run = dry_run

    def install(self, entry: dict, *, force: bool = False) -> None:
        name = entry["name"]
        pkg_type = entry.get("type", "npm")
        package = entry["package"]
        command = entry["command"]
        args = entry.get("args", [])

        self.console.print(f"\n[bold]Installing [cyan]{name}[/]...[/]")

        if pkg_type == "npm":
            self._install_npm(name, package, force)
        elif pkg_type == "python":
            self._install_python(name, package, force)
        else:
            self.console.print(f"[red]Unknown package type:[/] {pkg_type}")
            raise SystemExit(1)

        self.console.print(f"\n[green]Installed![/] Run it with:")
        self.console.print(f"  [bold]{command} {' '.join(args)}[/]")

        self._print_env_reminder(entry)

    def _install_npm(self, name: str, package: str, force: bool) -> None:
        if not shutil.which("npm") and not shutil.which("npx"):
            self.console.print("[red]npm/npx not found.[/] Install Node.js first: https://nodejs.org")
            raise SystemExit(1)

        if not self._is_npm_installed(package) or force:
            cmd = ["npm", "install", "-g", package]
            if self.dry_run:
                self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
                return
            self._run(cmd, f"Installing {package}...")
        else:
            self.console.print(f"  [dim]{package} already installed (use --force to reinstall)[/]")

    def _install_python(self, name: str, package: str, force: bool) -> None:
        ux = shutil.which("uvx") or shutil.which("uv")
        pip = shutil.which("pip3") or shutil.which("pip")

        if ux:
            cmd = ["uv", "tool", "install", package]
            if force:
                cmd.append("--force")
            if self.dry_run:
                self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
                return
            self._run(cmd, f"Installing {package} via uv...")
        elif pip:
            cmd = [pip, "install", "-U", package]
            if self.dry_run:
                self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
                return
            self._run(cmd, f"Installing {package} via pip...")
        else:
            self.console.print("[red]Neither uv nor pip found.[/]")
            raise SystemExit(1)

    def _is_npm_installed(self, package: str) -> bool:
        try:
            result = subprocess.run(
                ["npm", "list", "-g", package, "--depth=0"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run(self, cmd: list[str], message: str) -> None:
        self.console.print(f"  {message}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Command failed:[/] {' '.join(cmd)}")
            raise SystemExit(e.returncode)

    def _print_env_reminder(self, entry: dict) -> None:
        env_vars = entry.get("env", {})
        if not env_vars:
            return
        self.console.print("\n[yellow]This server needs environment variables:[/]")
        for key, val in env_vars.items():
            self.console.print(f"  [bold]{key}[/] = {val}")
        self.console.print("[dim]Set these before running, or we'll add 'em to your config.[/]")
