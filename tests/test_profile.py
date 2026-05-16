"""Tests for ProfileManager."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from mcphub.profile import ProfileManager


class TestProfileManager:
    def test_list_empty(self, tmp_path: Path):
        """list_all when profile dir is empty."""
        from mcphub import profile as profile_mod

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        mgr = ProfileManager(console=Console())
        with patch.object(profile_mod, "PROFILE_DIR", empty_dir):
            mgr.list_all()

    def test_delete_missing(self, tmp_path: Path):
        """delete a nonexistent profile."""
        from mcphub import profile as profile_mod

        mgr = ProfileManager(console=Console())
        with patch.object(profile_mod, "PROFILE_DIR", tmp_path):
            mgr.delete("no-such-profile")

    def test_save_no_servers(self):
        """save when no servers are configured."""
        with patch("mcphub.config.ConfigManager.list_servers", return_value={}):
            mgr = ProfileManager(console=Console())
            mgr.save("empty")

    def test_save_and_load_and_delete(self, tmp_path: Path):
        """Full cycle: save, verify file, load, delete."""
        from mcphub import profile as profile_mod
        from mcphub import config as config_mod

        fake_servers = {
            "claude": {
                "my-server": {
                    "command": "npx",
                    "args": ["-y", "pkg"],
                    "env": {"KEY": "val"},
                }
            }
        }

        profile_dir = tmp_path / "profiles"
        profile_dir.mkdir()

        with patch.object(profile_mod, "PROFILE_DIR", profile_dir), patch.object(
            config_mod.ConfigManager, "list_servers", return_value=fake_servers
        ), patch.object(config_mod.ConfigManager, "add_server", return_value=None):

            mgr = ProfileManager(console=Console())
            mgr.save("dev")

            profile_path = profile_dir / "dev.json"
            assert profile_path.exists()

            data = json.loads(profile_path.read_text())
            assert "claude" in data
            assert data["claude"]["my-server"]["command"] == "npx"

            mgr.load("dev")
            mgr.delete("dev")
            assert not profile_path.exists()

    def test_load_missing(self):
        """load a profile that doesn't exist."""
        mgr = ProfileManager(console=Console())
        mgr.load("nonexistent")
