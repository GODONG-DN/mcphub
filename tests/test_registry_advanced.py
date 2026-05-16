from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcphub.registry import REGISTRY, Registry


class TestRegistrySync:
    def test_sync_invalid_url_raises(self):
        r = Registry()
        with pytest.raises(RuntimeError):
            r.sync(url="https://does.not.exist.invalid/registry.json", timeout=2)

    def test_save_and_load_local(self, tmp_path: Path):
        r = Registry()
        cache = tmp_path / "registry.json"
        r.save_local(cache)
        assert cache.exists()

        r2 = Registry.load_local(cache)
        assert r2.count == r.count
        assert r2.get("filesystem") is not None

    def test_load_local_fallback(self, tmp_path: Path):
        missing = tmp_path / "does_not_exist.json"
        r = Registry.load_local(missing)
        assert r.count == len(REGISTRY)

    def test_load_local_invalid_json(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        r = Registry.load_local(bad)
        assert r.count == len(REGISTRY)

    def test_count_property(self):
        r = Registry()
        assert r.count == len(REGISTRY)


class TestRegistryEdgeCases:
    def test_empty_registry(self):
        r = Registry(entries=[])
        assert r.count == 0
        assert r.get("anything") is None
        assert r.list_all() == []
        assert r.search("anything") == []

    def test_duplicate_names_in_custom_entries(self):
        entries = [
            {
                "name": "dup",
                "description": "first",
                "repo": "x",
                "type": "npm",
                "package": "x",
                "command": "x",
                "args": [],
            },
            {
                "name": "dup",
                "description": "second",
                "repo": "x",
                "type": "npm",
                "package": "x",
                "command": "x",
                "args": [],
            },
        ]
        r = Registry(entries=entries)
        entry = r.get("dup")
        assert entry is not None
        # Last one wins in name-based index
        assert entry["description"] == "second"
