"""MCPHub TUI — interactive terminal browser for MCP servers."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from mcphub.registry import Registry


class ServerList(Static):
    """Displays the server list."""


class DetailPanel(Static):
    """Shows details of the selected server."""


class RegistryScreen(Screen):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("i", "install_server", "Install"),
        Binding("u", "uninstall_server", "Uninstall"),
        Binding("r", "run_server", "Run"),
        Binding("/", "focus_search", "Search"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.registry = Registry()
        self.servers = self.registry.list_all()
        self.selected_index = 0
        self._last_search = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="left-panel"):
                yield Input(placeholder="Search servers... (/ to focus)", id="search-input")
                yield ListView(id="server-list", *self._build_list_items())
            with Vertical(id="right-panel"):
                yield Static(id="detail-view")
        yield Footer()

    def _build_list_items(self) -> list[ListItem]:
        items = []
        for i, s in enumerate(self.servers):
            pkg_type = s.get("type", "npm").upper()
            label = f" {s['name']}  [{pkg_type}]"
            item = ListItem(Label(label), id=f"server-{i}")
            items.append(item)
        return items

    def _update_detail(self) -> None:
        if not self.servers:
            return
        entry = self.servers[self.selected_index]
        detail = self.query_one("#detail-view", Static)

        lines = [
            f"[bold cyan]{entry['name']}[/]",
            "",
            f"[dim]{entry['description']}[/]",
            "",
            f"[bold]Type:[/] {entry.get('type', 'npm').upper()}",
            f"[bold]Package:[/] {entry['package']}",
        ]
        if entry.get("repo") and entry["repo"] != "unknown":
            if entry["repo"].startswith("http"):
                lines.append(f"[bold]Repo:[/] {entry['repo']}")
            else:
                lines.append(f"[bold]Repo:[/] https://github.com/{entry['repo']}")
        lines.append(f"[bold]Command:[/] {entry['command']} {' '.join(entry.get('args', []))}")
        if entry.get("env"):
            lines.append("")
            lines.append("[bold]Env vars:[/]")
            for k, v in entry["env"].items():
                lines.append(f"  {k} = {v}")
        if entry.get("tags"):
            lines.append("")
            lines.append("[bold]Tags:[/] " + ", ".join(entry["tags"]))

        detail.update("\n".join(lines))

        # Highlight selected in list
        lv = self.query_one("#server-list", ListView)
        if 0 <= self.selected_index < len(lv.children):
            lv.index = self.selected_index

    def on_mount(self) -> None:
        if self.servers:
            self._update_detail()

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip().lower()
        if query == self._last_search:
            return
        self._last_search = query

        lv = self.query_one("#server-list", ListView)

        if query:
            self.servers = self.registry.search(query)
            self.servers += [s for s in self.registry.list_all() if s not in self.servers and query in s.get("description", "").lower()][:10]
        else:
            self.servers = self.registry.list_all()

        self.selected_index = 0
        lv.clear()
        lv.mount(*self._build_list_items())

        if self.servers:
            self._update_detail()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            try:
                idx = int(event.item.id.replace("server-", ""))
                self.selected_index = idx
                self._update_detail()
            except (ValueError, IndexError):
                pass

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_cursor_down(self) -> None:
        if not self.servers:
            return
        self.selected_index = min(self.selected_index + 1, len(self.servers) - 1)
        self._update_detail()

    def action_cursor_up(self) -> None:
        self.selected_index = max(self.selected_index - 1, 0)
        self._update_detail()

    def action_install_server(self) -> None:
        if not self.servers:
            return
        entry = self.servers[self.selected_index]
        self.app.push_screen(
            ConfirmScreen(
                f"Install [bold]{entry['name']}[/]?\n\n{entry['description']}",
                on_yes=lambda: self._do_install(entry),
            )
        )

    def _do_install(self, entry: dict) -> None:
        import subprocess
        from rich.console import Console

        c = Console()
        from mcphub.installer import Installer
        from mcphub.config import ConfigManager

        try:
            Installer(console=c).install(entry)
            ConfigManager(console=c).add_server(
                name=entry["name"],
                command=entry["command"],
                args=entry.get("args", []),
                env=entry.get("env", {}),
            )
        except Exception as e:
            self.notify(f"Install failed: {e}", severity="error")

    def action_uninstall_server(self) -> None:
        self.notify("Select a server and press 'u' to uninstall", severity="warning")

    def action_run_server(self) -> None:
        self.notify("Press 'r' to run — coming soon", severity="information")


class ConfirmScreen(Screen):
    def __init__(self, message: str, on_yes) -> None:
        super().__init__()
        self.message = message
        self.on_yes = on_yes

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.message, id="confirm-msg"),
            Horizontal(
                Button("Yes", variant="success", id="btn-yes"),
                Button("No", variant="error", id="btn-no"),
                id="confirm-buttons",
            ),
            id="confirm-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-yes":
            self.on_yes()
        self.app.pop_screen()


class McpHubTUI(App):
    TITLE = "MCPHub"
    SUB_TITLE = "MCP Server Manager"

    def on_mount(self) -> None:
        self.push_screen(RegistryScreen())


def run_tui() -> None:
    app = McpHubTUI()
    app.run()
