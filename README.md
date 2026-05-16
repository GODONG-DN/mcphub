# MCPHub

> **One-stop toolkit for the MCP ecosystem.**
> Install, configure, run, and build Model Context Protocol servers — from a single CLI.

<p align="center">
  <img src="https://img.shields.io/pypi/v/mcphub?color=success" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/mcphub" alt="Python">
  <img src="https://img.shields.io/github/license/GODONG-DN/mcphub" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/GODONG-DN/mcphub/ci.yml?branch=master" alt="CI">
</p>

---

## What's MCP?

[Model Context Protocol](https://modelcontextprotocol.io) (MCP) is an open protocol that lets AI models interact with external tools — file systems, databases, APIs, browsers, and more. Think of it as "USB-C for AI tools."

The problem? **Setting up MCP servers is a pain.** You need to:

1. Find the right server
2. Install it with the right package manager
3. Manually edit JSON config files for every AI client
4. Set up env vars and paths

MCPHub solves all four with a single command:

```
mcphub install github
```

---

## Quickstart

### Install

```bash
pip install mcphub
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install mcphub
```

### Usage

```bash
# sync the latest registry
mcphub sync

# see what's available
mcphub list

# search for something specific
mcphub search database

# install, auto-configure, and run
mcphub install postgres
mcphub run postgres

# look up details
mcphub info filesystem

# uninstall and clean up configs
mcphub uninstall postgres

# scaffold your own MCP server
mcphub dev my-cool-tool
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `mcphub list [--tag]` | List all available MCP servers |
| `mcphub search <kw>` | Search by name, description, or tag |
| `mcphub sync [--url]` | Pull the latest registry from remote |
| `mcphub info <name>` | Show details: repo, command, env vars |
| `mcphub install <name>` | Install and auto-configure AI clients |
| `mcphub run <name>` | Launch an installed MCP server |
| `mcphub uninstall <name>` | Remove the server and clean up configs |
| `mcphub config [--list]` | Show AI client config locations and entries |
| `mcphub dev <name>` | Scaffold a new MCP server project |

---

## Supported AI Clients

Auto-detect and auto-configure:

| Client | Supported |
|--------|----------|
| Claude Desktop | Yes |
| Cursor | Yes |
| Windsurf | Yes |
| Continue | Yes |

If your client isn't detected, `mcphub install` prints the exact JSON snippet to paste.

---

## Built-in Registry

17 MCP servers indexed out of the box:

| Category | Servers |
|----------|---------|
| **Official** | filesystem, github, brave-search, memory, puppeteer, postgres, slack, sqlite, docker, sequential-thinking, fetch, git, everything |
| **Community** | mcp-hfspace (HuggingFace), mermaid, notion, playwright |

Run `mcphub sync` to pull updates we add between releases.

---

## Build Your Own MCP Server

```bash
mcphub dev my-server
cd my-server
uv sync
uv run my_server
```

Gives you a working MCP server with a `hello` tool — ready to extend.

---

## Roadmap

- [ ] `mcphub test` — test tools against an MCP server
- [ ] Community registry submissions
- [ ] VS Code / JetBrains extensions
- [ ] Health-check dashboard for running servers

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

```bash
git clone https://github.com/GODONG-DN/mcphub.git
cd mcphub
pip install -e ".[dev]"
pytest
```

---

## License

MIT © [GoDon](https://github.com/GODONG-DN)
