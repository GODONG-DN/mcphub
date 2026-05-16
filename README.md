# MCPHub

> **One-stop toolkit for the MCP ecosystem.**
> Install, configure, and build Model Context Protocol servers — from a single CLI.

<p align="center">
  <img src="https://img.shields.io/pypi/v/mcphub?color=success" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/mcphub" alt="Python">
  <img src="https://img.shields.io/github/license/GODONG-DN/mcphub" alt="License">
</p>

---

## What is MCP?

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

### Basic usage

```bash
# see what's available
mcphub list

# search for something specific
mcphub search database

# install and auto-configure
mcphub install postgres

# look up details
mcphub info filesystem

# scaffold your own MCP server
mcphub dev my-cool-tool
```

---

## Why MCPHub?

| Before | After |
|---|---|
| Find server repos manually | `mcphub search <keyword>` |
| Read READMEs for install steps | `mcphub install <name>` |
| Manually hand-edit 3 JSON configs | Auto-configured on install |
| Debug env var issues | Reminders + auto-injection |
| Start from scratch every time | `mcphub dev` scaffolds a project |

---

## Supported AI Clients

MCPHub auto-detects and writes configs for:

| Client       | Config auto-detected |
|-------------|---------------------|
| Claude Desktop | Yes                  |
| Cursor         | Yes                  |
| Windsurf       | Soon                 |
| Continue       | Soon                 |

If your client isn't detected, `mcphub install` will print the exact JSON snippet to paste.

---

## Built-in Registry

Over a dozen MCP servers are indexed out of the box:

| Category   | Servers |
|-----------|---------|
| **Official** | filesystem, github, brave-search, memory, puppeteer, postgres, slack, sqlite, docker, sequential-thinking, fetch, git, everything |
| **Community** | mcp-hfspace (HuggingFace), mermaid, notion, playwright |

```bash
mcphub list
mcphub list --tag official
mcphub list --tag community
```

---

## Build Your Own MCP Server

```bash
mcphub dev my-server
cd my-server
uv sync
uv run my_server
```

This gives you a working MCP server with a `hello` tool — ready to extend.

---

## Roadmap

- [ ] Remote registry with community submissions
- [ ] `mcphub run` — one-command local server runner
- [ ] `mcphub test` — test tools against an MCP server
- [ ] VS Code extension for GUI installs
- [ ] Support for Windsurf, Continue, and Zed

---

## Contributing

Bug reports, feature requests, and PRs are welcome.

```bash
git clone https://github.com/GODONG-DN/mcphub.git
cd mcphub
pip install -e ".[dev]"
pytest
```

---

## License

MIT © [GoDon](https://github.com/GODONG-DN)
