"""Config manager — writes MCP server entries into AI client config files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rich.console import Console


def _resolve_claude_config() -> Path | None:
    """Find claude_desktop_config.json across platforms."""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming" / "Claude"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Claude"
    else:
        base = Path.home() / ".config" / "Claude"

    config_path = base / "claude_desktop_config.json"
    return config_path if config_path.exists() else None


def _resolve_cursor_config() -> Path | None:
    """Find the Cursor MCP config file."""
    if sys.platform == "win32":
        base = Path.home() / ".cursor"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
    else:
        base = Path.home() / ".config" / "Cursor" / "User" / "globalStorage"

    config_path = base / "mcp.json"
    if config_path.exists():
        return config_path

    # Cursor sometimes uses a versioned storage dir
    if sys.platform in ("win32", "linux") and base.parent.exists():
        for child in base.parent.iterdir():
            if child.is_dir() and "globalStorage" in child.name and child != base:
                candidate = child / "mcp.json"
                if candidate.exists():
                    return candidate

    return None


_CLIENTS = {
    "claude": {
        "name": "Claude Desktop",
        "resolver": _resolve_claude_config,
        "key": "mcpServers",
    },
    "cursor": {
        "name": "Cursor",
        "resolver": _resolve_cursor_config,
        "key": "mcpServers",
    },
}


class ConfigManager:
    """Reads and writes JSON config files for AI desktop clients."""

    def __init__(self, console: Console) -> None:
        self.console = console

    def add_server(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        for client_id, client_info in _CLIENTS.items():
            path = client_info["resolver"]()
            if path is None:
                continue

            self.console.print(f"\n[bold]Configuring [cyan]{client_info['name']}[/]...[/]")
            self._upsert_config(path, client_info["key"], name, command, args or [], env or {})

    def list_servers(self) -> dict[str, dict[str, dict]]:
        """Return all configured servers across all clients."""
        result: dict[str, dict[str, dict]] = {}
        for client_id, client_info in _CLIENTS.items():
            path = client_info["resolver"]()
            if path is None:
                continue
            config = self._read_json(path)
            result[client_id] = config.get(client_info["key"], {})
        return result

    def _upsert_config(
        self,
        config_path: Path,
        key: str,
        server_name: str,
        command: str,
        args: list[str],
        env: dict[str, str],
    ) -> None:
        config = self._read_json(config_path)

        if key not in config:
            config[key] = {}

        entry: dict = {"command": command, "args": args}
        if env:
            entry["env"] = env

        config[key][server_name] = entry

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            f.write("\n")

        self.console.print(f"  [green]+[/] [bold]{server_name}[/] → {config_path}")

    @staticmethod
    def _read_json(path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)
