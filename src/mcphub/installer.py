"""Installer — handles fetching and setting up MCP servers."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

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
        tags = entry.get("tags", [])
        clone_url = entry.get("repo", "")

        self.console.print(f"\n[bold]Installing [cyan]{name}[/]...[/]")

        if pkg_type == "npm":
            self._install_npm(name, package, force)
        elif pkg_type == "python":
            self._install_python(name, package, force)
        elif pkg_type == "repo":
            self._install_from_repo(name, clone_url, force)
        else:
            self.console.print(f"[red]Unknown package type:[/] {pkg_type}")
            raise SystemExit(1)

        from rich import box
        from rich.panel import Panel

        content = f"  [bold]{command} {' '.join(args)}[/]"
        if entry.get("env"):
            content += "\n[dim]  (see env vars below)[/]"

        self.console.print(
            Panel(content, title="[bold green]Installed[/]", border_style="green", box=box.ROUNDED)
        )
        self._print_env_reminder(entry)

    def _install_from_repo(self, name: str, url: str, force: bool) -> None:
        """Clone a GitHub repo and auto-detect install method."""
        if "github.com" not in url and "/" in url and not url.startswith("http"):
            url = f"https://github.com/{url}"

        if not url.startswith("http"):
            self.console.print(f"[red]Invalid repo URL:[/] {url}")
            raise SystemExit(1)

        if self.dry_run:
            self.console.print(f"  [dim](dry-run) Would clone:[/] {url}")
            self.console.print("  [dim](dry-run) Would auto-detect and install[/]")
            return

        tmp = Path(tempfile.mkdtemp(prefix="mcphub-"))
        try:
            self.console.print(f"  Cloning {url}...")
            subprocess.run(
                ["git", "clone", "--depth=1", url, str(tmp)],
                check=True,
                capture_output=True,
                text=True,
            )

            has_package_json = (tmp / "package.json").exists()
            has_pyproject = (tmp / "pyproject.toml").exists()
            has_setup_py = (tmp / "setup.py").exists()

            if has_package_json:
                self.console.print("  [dim]Detected npm project[/]")
                subprocess.run(
                    ["npm", "install", "-g", str(tmp)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            elif has_pyproject or has_setup_py:
                self.console.print("  [dim]Detected Python project[/]")
                pip = shutil.which("pip3") or shutil.which("pip")
                if pip:
                    subprocess.run(
                        [pip, "install", "-e", str(tmp)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                else:
                    self.console.print("[red]pip not found.[/]")
                    raise SystemExit(1)
            else:
                self.console.print(
                    "[yellow]Couldn't detect project type. Trying npm install...[/]"
                )
                subprocess.run(
                    ["npm", "install", "-g", str(tmp)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Failed to install from repo:[/] {e}")
            raise SystemExit(1)
        finally:
            try:
                shutil.rmtree(tmp, ignore_errors=True)
            except Exception:
                pass

    def _install_npm(self, name: str, package: str, force: bool) -> None:
        if not shutil.which("npm") and not shutil.which("npx"):
            self.console.print(
                "[red]npm/npx not found.[/] Install Node.js first: https://nodejs.org"
            )
            raise SystemExit(1)

        if self._is_npm_installed(package) and not force:
            self.console.print(f"  [dim]{package} already installed (use --force to reinstall)[/]")
            return

        cmd = ["npm", "install", "-g", package]
        if self.dry_run:
            self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
            return
        self._run_with_spinner(cmd, f"Installing {package}")

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
            self._run_with_spinner(cmd, f"Installing {package} via uv")
        elif pip:
            cmd = [pip, "install", "-U", package]
            if self.dry_run:
                self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
                return
            self._run_with_spinner(cmd, f"Installing {package} via pip")
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

    def _run_with_spinner(self, cmd: list[str], status_msg: str) -> None:
        from rich.status import Status

        with self.console.status(f"[bold]{status_msg}[/]", spinner="dots"):
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                self.console.print(f"[red]Command failed:[/] {' '.join(cmd)}")
                if e.stderr:
                    self.console.print(f"[dim]{e.stderr.strip()}[/]")
                raise SystemExit(e.returncode)

    def _print_env_reminder(self, entry: dict) -> None:
        env_vars = entry.get("env", {})
        if not env_vars:
            return
        self.console.print()
        self.console.print("[yellow]This server needs environment variables:[/]")
        for key, val in env_vars.items():
            self.console.print(f"  [bold]{key}[/] = {val}")
        self.console.print("[dim]Set these in your env or they'll be added to your client config.[/]")


class Uninstaller:
    """Removes MCP servers and cleans up."""

    def __init__(self, console: Console, dry_run: bool = False) -> None:
        self.console = console
        self.dry_run = dry_run

    def uninstall(self, entry: dict) -> None:
        name = entry["name"]
        pkg_type = entry.get("type", "npm")
        package = entry["package"]

        self.console.print(f"\n[bold]Uninstalling [cyan]{name}[/]...[/]")

        if pkg_type == "npm":
            self._uninstall_npm(package)
        elif pkg_type == "python":
            self._uninstall_python(package)
        else:
            self.console.print(f"[red]Unknown package type:[/] {pkg_type}")
            raise SystemExit(1)

        self.console.print(f"  [green]Removed {name}[/]")

    def _uninstall_npm(self, package: str) -> None:
        if not shutil.which("npm"):
            self.console.print("[yellow]npm not found, skipping npm uninstall.[/]")
            return

        cmd = ["npm", "uninstall", "-g", package]
        if self.dry_run:
            self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
            return
        self._run(cmd, f"Removing {package}...")

    def _uninstall_python(self, package: str) -> None:
        uv = shutil.which("uv")
        pip = shutil.which("pip3") or shutil.which("pip")

        if uv:
            cmd = ["uv", "tool", "uninstall", package]
            if self.dry_run:
                self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
                return
            self._run(cmd, f"Removing {package} via uv...")
        elif pip:
            cmd = [pip, "uninstall", "-y", package]
            if self.dry_run:
                self.console.print(f"  [dim](dry-run) Would run:[/] {' '.join(cmd)}")
                return
            self._run(cmd, f"Removing {package} via pip...")

    def _run(self, cmd: list[str], message: str) -> None:
        self.console.print(f"  {message}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            self.console.print(f"[yellow]Command may have already been removed:[/] {' '.join(cmd)}")
