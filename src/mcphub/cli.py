"""MCPHub CLI — the main entrypoint."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mcphub.config import ConfigManager
from mcphub.installer import Installer
from mcphub.registry import Registry
from mcphub.scaffold import Scaffolder

app = typer.Typer(
    name="mcphub",
    help="MCP ecosystem toolkit — install, configure, and build MCP servers",
    no_args_is_help=True,
)

console = Console()
registry = Registry()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold]mcphub[/] version [cyan]{__import__('mcphub').__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    pass


# -------------------------------------------------------
#  install
# -------------------------------------------------------

@app.command()
def install(
    name: str = typer.Argument(..., help="MCP server name to install"),
    force: bool = typer.Option(False, "--force", "-f", help="Reinstall even if already present"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without actually doing it"
    ),
) -> None:
    """Install an MCP server from the registry."""
    entry = registry.get(name)
    if entry is None:
        console.print(f"[red]Unknown server:[/] {name}")
        suggestions = registry.search(name, fuzzy=True)
        if suggestions:
            table = Table(title="Did you mean?", show_header=False, box=None)
            for hit in suggestions:
                table.add_row(f"  [cyan]mcphub install {hit['name']}[/]  {hit['description']}")
            console.print(table)
        raise typer.Exit(1)

    installer = Installer(console=console, dry_run=dry_run)
    installer.install(entry, force=force)

    config = ConfigManager(console=console)
    config.add_server(
        name=entry["name"],
        command=entry["command"],
        args=entry.get("args", []),
        env=entry.get("env", {}),
    )


# -------------------------------------------------------
#  search
# -------------------------------------------------------

@app.command()
def search(
    query: str = typer.Argument("", help="Search term (empty = list all)"),
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Search available MCP servers."""
    results = registry.list_all(tag=tag) if not query else registry.search(query)

    if json_output:
        import json as _json

        console.print(_json.dumps(results, indent=2))
        return

    if not results:
        console.print(f"[yellow]No servers found for [bold]{query}[/][/]")
        return

    for entry in results:
        tags_text = " ".join(f"[dim]#{t}[/]" for t in entry.get("tags", []))
        pkg_type = entry.get("type", "npm").upper()
        console.print(f"  [cyan bold]{entry['name']}[/]  [dim]({pkg_type})[/]")
        console.print(f"    {entry['description']}")
        console.print(f"    {tags_text}")
        console.print()


# -------------------------------------------------------
#  list
# -------------------------------------------------------

@app.command()
def list(
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tag"),
) -> None:
    """List all available MCP servers."""
    results = registry.list_all(tag=tag)

    table = Table(title=None, show_header=True, header_style="bold")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Description")
    table.add_column("Tags")

    for entry in results:
        pkg_type = entry.get("type", "npm")
        tags_str = ", ".join(entry.get("tags", [])[:3])
        table.add_row(entry["name"], pkg_type, entry["description"], tags_str)

    console.print(f"\n[bold]{len(results)} MCP servers")
    if tag:
        console.print(f"[dim]Filtered by tag: #{tag}[/]")
    console.print()
    console.print(table)


# -------------------------------------------------------
#  info
# -------------------------------------------------------

@app.command()
def info(
    name: str = typer.Argument(..., help="MCP server name"),
) -> None:
    """Show detailed info about an MCP server."""
    entry = registry.get(name)
    if entry is None:
        console.print(f"[red]Unknown server:[/] {name}")
        raise typer.Exit(1)

    panel_content = Text()
    panel_content.append(f"  Name:        {entry['name']}\n")
    panel_content.append(f"  Description: {entry['description']}\n")
    panel_content.append(f"  Type:        {entry.get('type', 'npm')}\n")
    panel_content.append(f"  Package:     {entry['package']}\n")
    panel_content.append(f"  Repository:  https://github.com/{entry['repo']}\n")
    if "subdir" in entry:
        panel_content.append(f"  Subdir:      {entry['subdir']}\n")
    panel_content.append(f"  Command:     {entry['command']} {' '.join(entry.get('args', []))}\n")
    if entry.get("env"):
        panel_content.append(f"  Env vars:\n")
        for k, v in entry["env"].items():
            panel_content.append(f"    {k} = {v}\n")

    console.print()
    console.print(Panel(panel_content, title=f"[bold cyan]{name}[/]", border_style="cyan"))


# -------------------------------------------------------
#  config
# -------------------------------------------------------

@app.command()
def config(
    _list: bool = typer.Option(False, "--list", "-l", help="List configured servers"),
) -> None:
    """Manage MCP configurations for AI clients."""
    mgr = ConfigManager(console=console)

    if _list:
        all_servers = mgr.list_servers()
        if not all_servers:
            console.print("[yellow]No AI clients with MCP config found.[/]")
            return

        for client_id, servers in all_servers.items():
            console.print(f"\n[bold]{client_id}[/]")
            if not servers:
                console.print("  [dim](no servers configured)[/]")
                continue
            for name, entry in servers.items():
                console.print(f"  [cyan]{name}[/] → {entry.get('command', '?')}")
        console.print()
        return

    console.print("\n[bold]MCP client config locations:[/]\n")
    from mcphub.config import _CLIENTS

    for client_id, info in _CLIENTS.items():
        path = info["resolver"]()
        status = "[green]found[/]" if path else "[dim]not found[/]"
        display_path = str(path) if path else f"(expected: {info['name']} config dir)"
        console.print(f"  [cyan]{info['name']}[/]  {status}")
        console.print(f"    {display_path}")


# -------------------------------------------------------
#  dev
# -------------------------------------------------------

@app.command()
def dev(
    name: str = typer.Argument(..., help="Name for the new MCP server project"),
    target: str = typer.Option(None, "--target", "-t", help="Directory to create the project in"),
) -> None:
    """Scaffold a new MCP server project."""
    scaffolder = Scaffolder(console=console)
    scaffolder.create(name, target_dir=target)


if __name__ == "__main__":
    app()
