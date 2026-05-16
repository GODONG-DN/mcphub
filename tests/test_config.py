"""Tests for ConfigManager — AI client config handling."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from mcphub.config import ConfigManager, _CLIENTS, _resolve_claude_config, _resolve_cursor_config


class TestConfigResolvers:
    def test_claude_resolver_returns_path_or_none(self):
        result = _resolve_claude_config()
        assert result is None or isinstance(result, Path)

    def test_cursor_resolver_returns_path_or_none(self):
        result = _resolve_cursor_config()
        assert result is None or isinstance(result, Path)

    def test_clients_dict_structure(self):
        required = {"name", "resolver", "key"}
        for client_id, info in _CLIENTS.items():
            missing = required - set(info.keys())
            assert not missing, f"{client_id} missing keys: {missing}"


class TestConfigManager:
    def test_read_json_missing_file(self, tmp_path: Path):
        result = ConfigManager._read_json(tmp_path / "nonexistent.json")
        assert result == {}

    def test_read_json_valid(self, tmp_path: Path):
        path = tmp_path / "config.json"
        path.write_text('{"mcpServers": {"gh": {"command": "test"}}}')
        result = ConfigManager._read_json(path)
        assert result["mcpServers"]["gh"]["command"] == "test"

    def test_add_and_remove_server_cycle(self, tmp_path: Path):
        """Add a server, verify it's in the config, then remove it."""
        from rich.console import Console
        from mcphub import config as config_mod

        config_path = tmp_path / "mcp.json"
        config_path.write_text("{}")

        fake_client = {
            "test": {
                "name": "TestClient",
                "resolver": lambda p=config_path: p,
                "key": "mcpServers",
            },
        }

        with patch.object(config_mod, "_CLIENTS", fake_client):
            mgr = ConfigManager(console=Console())
            mgr.add_server(
                name="my-server",
                command="npx",
                args=["-y", "my-pkg"],
                env={"KEY": "val"},
            )

            data = json.loads(config_path.read_text())
            assert "my-server" in data["mcpServers"]
            assert data["mcpServers"]["my-server"]["command"] == "npx"
            assert data["mcpServers"]["my-server"]["env"]["KEY"] == "val"

            mgr.remove_server("my-server")

            data = json.loads(config_path.read_text())
            assert "my-server" not in data["mcpServers"]
