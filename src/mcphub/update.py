"""Check for new versions of mcphub on PyPI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from packaging.version import Version


@dataclass
class UpdateInfo:
    current: str
    latest: str
    is_outdated: bool
    url: str


def check_version(
    current: str,
    cache_path: Path,
    ttl: int = 86400,
    timeout: float = 3,
) -> UpdateInfo | None:
    """Check PyPI for newer versions, caching the result for `ttl` seconds.

    Returns None if the check couldn't complete (network error, etc.).
    """
    # Don't spam pypi — use a cache file
    now = __import__("time").time()
    if cache_path.exists() and (now - cache_path.stat().st_mtime) < ttl:
        return None  # checked recently, skip

    try:
        resp = httpx.get(
            "https://pypi.org/pypi/mcphub/json",
            timeout=timeout,
            follow_redirects=True,
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        latest = data["info"]["version"]
    except Exception:
        return None

    # Update the cache timestamp
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(latest)

    info = UpdateInfo(
        current=current,
        latest=latest,
        is_outdated=Version(latest) > Version(current),
        url="https://pypi.org/project/mcphub/",
    )
    return info
