"""Tests for Runner."""

from __future__ import annotations


class TestRunner:
    def test_runner_dry_run_npm(self):
        from rich.console import Console

        from mcphub.runner import Runner

        runner = Runner(console=Console(), dry_run=True)
        entry = {
            "name": "test",
            "command": "npx",
            "args": ["-y", "test-pkg"],
            "env": {"TOKEN": "<your-token>"},
        }
        runner.run(entry)  # dry-run: should print, not execute

    def test_runner_sets_env_vars(self):
        import os

        from rich.console import Console

        from mcphub.runner import Runner

        os.environ["MCP_TEST_EXISTING"] = "real-value"
        runner = Runner(console=Console(), dry_run=True)

        entry = {
            "name": "test",
            "command": "echo",
            "args": ["hello"],
            "env": {"MCP_TEST_EXISTING": "<placeholder>", "MCP_TEST_NEW": "new-val"},
        }
        runner.run(entry)
        del os.environ["MCP_TEST_EXISTING"]
