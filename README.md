# MCPHub

> **One-stop toolkit for the MCP ecosystem.**
> Install, configure, run, and build Model Context Protocol servers �?from a single CLI.

<p align="center">
  <img src="https://img.shields.io/pypi/v/mcphub?color=success" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/mcphub" alt="Python">
  <img src="https://img.shields.io/github/license/GODONG-DNG-DN/mcphub" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/GODONG-DNG-DN/mcphub/ci.yml?branch=master" alt="CI">
</p>

---

## What's MCP?

[Model Context Protocol](https://modelcontextprotocol.io) (MCP) is an open protocol that lets AI models interact with external tools �?file systems, databases, APIs, browsers, and more. Think of it as "USB-C for AI tools."

The problem? **Setting up MCP servers is a pain.** You need to:

1. Find the right server
2. Install it with the right package manager
3. Manually edit JSON config files for every AI client
4. Set up env vars and paths

MCPHub solves all four with a single command:

```
mcphub install github
```

**Or install anything** �?even if it's not in our registry:

```
mcphub install @anthropic/server-filesystem     # any npm package
mcphub install my-mcp-tool --type python         # any pip package
mcphub install user/repo --type repo             # any GitHub repo
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
| `mcphub sync` | Pull the latest registry from remote |
| `mcphub info <name>` | Show details: repo, command, env vars |
| `mcphub install <target>` | Install from registry / npm / pip / GitHub repo |
| `mcphub run <name>` | Launch an installed MCP server |
| `mcphub test <name>` | Connect and list all tools a server exposes |
| `mcphub uninstall <name>` | Remove the server and clean up configs |
| `mcphub config [--list]` | Show AI client config locations and entries |
| `mcphub profile` | Save/load/delete sets of server configs |
| `mcphub dev <name>` | Scaffold a new MCP server project |
| `mcphub doctor` | Check your system for MCP prerequisites |
| `mcphub tui` | Launch interactive terminal UI (needs `pip install mcphub[tui]`) |

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

27 MCP servers indexed out of the box:

| Category | Servers |
|----------|---------|
| **Official** | filesystem, github, brave-search, memory, puppeteer, postgres, slack, sqlite, docker, sequential-thinking, fetch, git, everything, google-maps, youtube, everart |
| **Community** | mcp-hfspace, mermaid, notion, playwright, exa, tavily, perplexity, figma, linear, obsidian, jira |

Run `mcphub sync` to pull updates we add between releases.

---

## Build Your Own MCP Server

```bash
mcphub dev my-server
cd my-server
uv sync
uv run my_server
```

Gives you a working MCP server with a `hello` tool �?ready to extend.

---

## Roadmap

- [ ] Community registry submissions via PR
- [ ] VS Code extension with GUI
- [ ] Web dashboard for managing running servers
- [ ] `mcphub publish` �?push your own server to the registry

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

```bash
git clone https://github.com/GODONG-DNG-DN/mcphub.git
cd mcphub
pip install -e ".[dev]"
pytest
```

---

## License

MIT © [GODONG-DN](https://github.com/GODONG-DNG-DN)

