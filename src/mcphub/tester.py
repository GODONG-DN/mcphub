"""Lightweight MCP protocol tester — lists and calls tools."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def _send_rpc(proc: subprocess.Popen, request: dict, timeout: float = 5) -> dict:
    """Send a JSON-RPC request over stdin and read the response from stdout."""
    payload = json.dumps(request) + "\n"

    try:
        proc.stdin.write(payload)
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
        return {"error": "Broken pipe — server may have crashed on startup"}

    line = ""
    try:
        proc.stdout.readline() if proc.stdout else None
        line = proc.stdout.readline() if proc.stdout else ""
    except Exception as exc:
        return {"error": f"Read error: {exc}"}

    if not line or not line.strip():
        return {"error": "No response from server"}

    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response: {line[:200]}"}


def list_tools(console: Console, entry: dict) -> dict[str, Any] | None:
    """Connect to an MCP server and list its tools."""
    command = entry["command"]
    args = entry.get("args", [])
    cmd = [command] + args

    console.print(f"\n[bold]Connecting to [cyan]{entry['name']}[/]...[/]")
    console.print(f"  [dim]{' '.join(cmd)}[/]")

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        console.print(f"[red]Command not found:[/] {command}")
        return None

    # Initialize
    init_resp = _send_rpc(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcphub", "version": "0.4.0"},
            },
        },
    )

    if "error" in init_resp:
        console.print(f"[red]Initialize failed:[/] {init_resp.get('error') or init_resp.get('error')}")

    # Send initialized notification
    try:
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
        pass

    # List tools
    tools_resp = _send_rpc(
        proc,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )

    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        proc.kill()

    if "error" in tools_resp:
        console.print(f"[red]Failed to list tools:[/] {tools_resp.get('error')}")
        if stderr_output := _read_stderr(proc):
            console.print(f"[dim]Server stderr: {stderr_output[:500]}[/]")
        return None

    tools = tools_resp.get("result", {}).get("tools", [])
    return tools


def _read_stderr(proc: subprocess.Popen) -> str:
    try:
        if proc.stderr and proc.stderr.readable():
            return proc.stderr.read()
    except Exception:
        pass
    return ""


def run_test(console: Console, entry: dict) -> None:
    """Run a tool listing test against an MCP server."""
    from rich import box

    tools = list_tools(console, entry)

    if tools is None:
        return

    if not tools:
        console.print("[yellow]No tools exposed by this server.[/]")
        return

    console.print(f"\n[green]{len(tools)} tool(s) found[/] for [bold cyan]{entry['name']}[/]:")

    for tool in tools:
        name = tool.get("name", "?")
        desc = tool.get("description", "no description")
        params = tool.get("inputSchema", {}).get("properties", {})
        required = tool.get("inputSchema", {}).get("required", [])

        console.print()
        console.print(f"  [cyan bold]{name}[/]")
        console.print(f"    [dim]{desc}[/]")

        if params:
            console.print("    [bold]Parameters:[/]")
            for param_name, param_info in params.items():
                ptype = param_info.get("type", "any")
                pdesc = param_info.get("description", "")
                req_mark = "[red]*[/]" if param_name in required else ""
                console.print(f"      {param_name}{req_mark}: [dim]{ptype}[/] — {pdesc}")

    console.print()
    console.print(
        Panel(
            f"[dim]To call a tool, connect an MCP client (Claude Desktop, Cursor, etc.)[/]\n"
            f"[dim]with the config written by `mcphub install {entry['name']}`[/]",
            border_style="dim",
            box=box.MINIMAL,
        )
    )
