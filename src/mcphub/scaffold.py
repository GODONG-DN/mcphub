"""Scaffolder — generates new MCP server projects."""

from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console

_DEFAULT_TEMPLATE = """\"\"\"
{caps_name} MCP server — {description}
\"\"\"

import asyncio
import json
import os

from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent


server = Server("{name}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="{name}_hello",
            description="Say hello — a simple starter tool",
            inputSchema={{
                "type": "object",
                "properties": {{
                    "name": {{
                        "type": "string",
                        "description": "Who to greet",
                    }},
                }},
                "required": ["name"],
            }},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "{name}_hello":
        who = arguments.get("name", "world")
        return [TextContent(type="text", text=f"Hello, {{who}}! from {caps_name}")]

    raise ValueError(f"Unknown tool: {{name}}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
"""


class Scaffolder:
    """Generates a new MCP server project from scratch."""

    def __init__(self, console: Console) -> None:
        self.console = console

    def create(self, name: str, target_dir: str | None = None) -> Path:
        root = Path(target_dir or name).resolve()

        if root.exists() and any(root.iterdir()):
            self.console.print(f"[red]{root} already exists and isn't empty.[/]")
            raise SystemExit(1)

        root.mkdir(parents=True, exist_ok=True)
        pkg_dir = root / name.replace("-", "_")

        self.console.print(f"\n[bold]Scaffolding MCP server [cyan]{name}[/]...[/]")

        self._write_server_module(pkg_dir, name)
        self._write_pyproject(root, name)
        self._write_readme(root, name)
        self._init_git(root)

        self.console.print(f"\n[green]Done![/] Your server is ready at {root}")
        self.console.print(f"\n  cd {name}")
        self.console.print(f"  uv sync")
        self.console.print(f"  uv run {name.replace('-', '_')}")

        return root

    def _write_server_module(self, pkg_dir: Path, name: str) -> None:
        pkg_dir.mkdir(parents=True, exist_ok=True)

        init_file = pkg_dir / "__init__.py"
        init_file.write_text(
            _DEFAULT_TEMPLATE.format(
                name=name,
                caps_name=name.upper().replace("-", "_"),
                description=f"A {name} MCP server",
            ),
            encoding="utf-8",
        )
        self.console.print(f"  [green]+[/] {init_file}")

    def _write_pyproject(self, root: Path, name: str) -> None:
        pyproject = f"""[project]
name = "{name}"
version = "0.1.0"
description = "MCP server: {name}"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0",
]

[project.scripts]
{name} = "{name.replace('-', '_')}:main"
"""

        path = root / "pyproject.toml"
        path.write_text(pyproject, encoding="utf-8")
        self.console.print(f"  [green]+[/] {path}")

    def _write_readme(self, root: Path, name: str) -> None:
        readme = f"""# {name}

An MCP server.

## Quickstart

    pip install {name}
    {name}

Or use uv:

    uv sync
    uv run {name}

## Client config

Add to your AI client's config:

```json
{{
    "mcpServers": {{
        "{name}": {{
            "command": "uv",
            "args": ["--directory", "/path/to/{name}", "run", "{name.replace('-', '_')}"]
        }}
    }}
}}
```
"""
        path = root / "README.md"
        path.write_text(readme, encoding="utf-8")
        self.console.print(f"  [green]+[/] {path}")

    def _init_git(self, root: Path) -> None:
        try:
            subprocess.run(
                ["git", "init", str(root)],
                capture_output=True,
                check=False,
            )
            self.console.print("  [dim]git init[/]")
        except Exception:
            pass
