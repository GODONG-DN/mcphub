from __future__ import annotations

from mcphub.registry import REGISTRY, Registry


class TestRegistry:
    def test_get_existing(self):
        r = Registry()
        assert r.get("filesystem") is not None
        assert r.get("github") is not None

    def test_get_missing(self):
        r = Registry()
        assert r.get("not-a-real-server") is None

    def test_get_case_insensitive(self):
        r = Registry()
        assert r.get("FileSystem") is not None
        assert r.get("GITHUB") is not None

    def test_search_exact(self):
        r = Registry()
        results = r.search("postgres")
        assert len(results) >= 1
        assert any(e["name"] == "postgres" for e in results)

    def test_search_fuzzy(self):
        r = Registry()
        results = r.search("postgrest", fuzzy=True)
        assert any(e["name"] == "postgres" for e in results)

    def test_list_all(self):
        r = Registry()
        entries = r.list_all()
        assert len(entries) == len(REGISTRY)

    def test_list_by_tag(self):
        r = Registry()
        entries = r.list_all(tag="official")
        assert len(entries) > 0
        assert all("official" in e.get("tags", []) for e in entries)

    def test_custom_entries(self):
        custom = [
            {
                "name": "my-server",
                "description": "test",
                "repo": "me/test",
                "type": "npm",
                "package": "test-pkg",
                "command": "npx",
                "args": [],
            }
        ]
        r = Registry(entries=custom)
        assert r.get("my-server") is not None
        assert r.get("other") is None
