"""Registry of known MCP servers."""

from __future__ import annotations

import json
from difflib import get_close_matches
from pathlib import Path
from typing import Any

import httpx

REMOTE_REGISTRY_URL = (
    "https://raw.githubusercontent.com/GODONG-DN/mcphub/master/registry.json"
)

REGISTRY = [
    {
        "name": "filesystem",
        "description": "Secure file operations with configurable access controls",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/filesystem",
        "type": "npm",
        "package": "@modelcontextprotocol/server-filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
        "tags": ["files", "storage", "official"],
    },
    {
        "name": "github",
        "description": "GitHub API integration — repos, issues, PRs, and more",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/github",
        "type": "npm",
        "package": "@modelcontextprotocol/server-github",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"},
        "tags": ["github", "git", "api", "official"],
    },
    {
        "name": "brave-search",
        "description": "Web search via Brave Search API, with local fallback",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/brave-search",
        "type": "npm",
        "package": "@modelcontextprotocol/server-brave-search",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": "<your-key>"},
        "tags": ["search", "web", "official"],
    },
    {
        "name": "memory",
        "description": "Knowledge-graph-based persistent memory system",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/memory",
        "type": "npm",
        "package": "@modelcontextprotocol/server-memory",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "tags": ["memory", "knowledge-graph", "official"],
    },
    {
        "name": "puppeteer",
        "description": "Browser automation — screenshots, scraping, and web interaction",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/puppeteer",
        "type": "npm",
        "package": "@modelcontextprotocol/server-puppeteer",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "tags": ["browser", "automation", "official"],
    },
    {
        "name": "postgres",
        "description": "PostgreSQL database introspection and querying",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/postgres",
        "type": "npm",
        "package": "@modelcontextprotocol/server-postgres",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"],
        "env": {"DATABASE_URL": "<connection-string>"},
        "tags": ["database", "sql", "official"],
    },
    {
        "name": "slack",
        "description": "Slack workspace integration — channels, messages, and users",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/slack",
        "type": "npm",
        "package": "@modelcontextprotocol/server-slack",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {"SLACK_BOT_TOKEN": "<your-token>"},
        "tags": ["slack", "messaging", "official"],
    },
    {
        "name": "sqlite",
        "description": "SQLite database interaction and exploration",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/sqlite",
        "type": "npm",
        "package": "@modelcontextprotocol/server-sqlite",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite"],
        "tags": ["database", "sqlite", "official"],
    },
    {
        "name": "docker",
        "description": "Docker container management via MCP",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/docker",
        "type": "npm",
        "package": "@modelcontextprotocol/server-docker",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-docker"],
        "tags": ["docker", "containers", "infra", "official"],
    },
    {
        "name": "sequential-thinking",
        "description": "Dynamic thought chains for complex reasoning",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/sequential-thinking",
        "type": "npm",
        "package": "@modelcontextprotocol/server-sequential-thinking",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "tags": ["reasoning", "thinking", "official"],
    },
    {
        "name": "fetch",
        "description": "Fetch and convert URLs to markdown, respecting robots.txt",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/fetch",
        "type": "npm",
        "package": "@modelcontextprotocol/server-fetch",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
        "tags": ["web", "fetch", "scraping", "official"],
    },
    {
        "name": "git",
        "description": "Direct Git repository operations via MCP",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/git",
        "type": "npm",
        "package": "@modelcontextprotocol/server-git",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git"],
        "tags": ["git", "vcs", "official"],
    },
    {
        "name": "everything",
        "description": "Reference server — every MCP feature in one place",
        "repo": "modelcontextprotocol/servers",
        "subdir": "src/everything",
        "type": "npm",
        "package": "@modelcontextprotocol/server-everything",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-everything"],
        "tags": ["reference", "demo", "official"],
    },
    # Community servers
    {
        "name": "mcp-hfspace",
        "description": "Use HuggingFace Spaces directly from MCP clients",
        "repo": "evalstate/mcp-hfspace",
        "type": "npm",
        "package": "@llmindset/mcp-hfspace",
        "command": "npx",
        "args": ["-y", "@llmindset/mcp-hfspace"],
        "tags": ["huggingface", "ai", "community"],
    },
    {
        "name": "mermaid",
        "description": "Generate Mermaid diagrams through natural language",
        "repo": "pab1it0/mermaid-mcp-server",
        "type": "python",
        "package": "mermaid-mcp-server",
        "command": "uvx",
        "args": ["mermaid-mcp-server"],
        "tags": ["diagrams", "visualization", "community"],
    },
    {
        "name": "notion",
        "description": "Notion API integration for pages, databases, and blocks",
        "repo": "suekou/mcp-notion-server",
        "type": "npm",
        "package": "@suekou/mcp-notion-server",
        "command": "npx",
        "args": ["-y", "@suekou/mcp-notion-server"],
        "env": {"NOTION_API_TOKEN": "<your-token>"},
        "tags": ["notion", "docs", "community"],
    },
    {
        "name": "playwright",
        "description": "Headless browser testing and scraping with Playwright",
        "repo": "executeautomation/mcp-playwright",
        "type": "npm",
        "package": "@executeautomation/playwright-mcp-server",
        "command": "npx",
        "args": ["-y", "@executeautomation/playwright-mcp-server"],
        "tags": ["browser", "testing", "community"],
    },
]


class Registry:
    """Registry that merges built-in entries with optional remote listings."""

    def __init__(self, entries: list[dict] | None = None) -> None:
        self._entries = entries if entries is not None else list(REGISTRY)
        self._by_name: dict[str, dict] = {e["name"].lower(): e for e in self._entries}

    @property
    def count(self) -> int:
        return len(self._entries)

    def get(self, name: str) -> dict | None:
        return self._by_name.get(name.lower())

    def search(self, query: str, *, fuzzy: bool = False, limit: int = 5) -> list[dict]:
        q = query.lower()
        results = []

        if fuzzy:
            names = [e["name"] for e in self._entries]
            matches = get_close_matches(q, names, n=limit, cutoff=0.4)
            seen = set()
            for name in matches:
                entry = self._by_name[name]
                if name not in seen:
                    seen.add(name)
                    results.append(entry)
            return results

        for entry in self._entries:
            if q in entry["name"] or q in entry["description"].lower():
                results.append(entry)
                continue
            for tag in entry.get("tags", []):
                if q in tag:
                    results.append(entry)
                    break

        return results[:limit]

    def list_all(self, tag: str | None = None) -> list[dict]:
        if tag is None:
            return list(self._entries)
        return [e for e in self._entries if tag in e.get("tags", [])]

    def sync(
        self,
        url: str = REMOTE_REGISTRY_URL,
        timeout: float = 10,
    ) -> int:
        """Fetch remote entries and merge into the local list.

        Returns how many new entries were added.
        """
        try:
            resp = httpx.get(url, timeout=timeout)
            resp.raise_for_status()
            remote = resp.json()
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch registry from {url}: {exc}") from exc

        if not isinstance(remote, list):
            raise ValueError("Remote registry must be a JSON array of entries")

        existing = set(self._by_name.keys())
        added = 0

        for entry in remote:
            name = entry.get("name", "").lower()
            if not name:
                continue
            if name not in existing:
                self._entries.append(entry)
                self._by_name[name] = entry
                existing.add(name)
                added += 1

        return added

    def save_local(self, path: Path) -> None:
        """Persist the full registry to a local JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, indent=2)

    @classmethod
    def load_local(cls, path: Path) -> Registry:
        """Create a Registry from a local JSON file, falling back to built-in."""
        try:
            with open(path, encoding="utf-8") as f:
                entries = json.load(f)
            return cls(entries=entries)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()
