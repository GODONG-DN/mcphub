"""Tests for Installer and Uninstaller."""

from __future__ import annotations

import shutil


class TestInstaller:
    def test_installer_dry_run_npm(self):
        from unittest.mock import patch

        from rich.console import Console

        from mcphub.installer import Installer

        installer = Installer(console=Console(), dry_run=True)
        entry = {
            "name": "test-pkg",
            "type": "npm",
            "package": "some-pkg",
            "command": "npx",
            "args": ["-y", "some-pkg"],
        }

        with patch.object(Installer, "_is_npm_installed", return_value=False):
            installer.install(entry)

    def test_installer_dry_run_python(self):
        from unittest.mock import patch

        from rich.console import Console

        from mcphub.installer import Installer

        installer = Installer(console=Console(), dry_run=True)
        entry = {
            "name": "test-pkg",
            "type": "python",
            "package": "some-pip-pkg",
            "command": "uvx",
            "args": ["some-pip-pkg"],
        }

        with patch.object(shutil, "which", return_value="/usr/bin/uv"):
            installer.install(entry)

    def test_is_npm_installed_handles_error(self):
        from rich.console import Console

        from mcphub.installer import Installer

        installer = Installer(console=Console())
        # Should not crash, return False
        result = installer._is_npm_installed("definitely-not-installed-xyz123")
        assert result is False


class TestUninstaller:
    def test_uninstall_dry_run(self):
        from rich.console import Console

        from mcphub.installer import Uninstaller

        uninstaller = Uninstaller(console=Console(), dry_run=True)
        entry = {
            "name": "test-pkg",
            "type": "npm",
            "package": "some-pkg",
        }
        uninstaller.uninstall(entry)
