"""Wait until a deployed static site serves the expected Nuxt build.

GitHub Pages' CDN may keep serving the previous build for a short while after a
deployment. The post-deploy smoke test must check the build that was just
published, so it first waits for `_nuxt/builds/latest.json` to report that build's id.

Usage: python scripts/wait_for_pages_build.py <site-url> <build-id> [--timeout 300] [--interval 10]
       python scripts/wait_for_pages_build.py --local-id apps/web/.output/public
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path
from collections.abc import Callable
from typing import Any, Protocol

MANIFEST = "_nuxt/builds/latest.json"


class Clock(Protocol):
    def time(self) -> float: ...

    def sleep(self, seconds: float) -> None: ...


def local_build_id(root: Path) -> str:
    return str(json.loads((root / MANIFEST).read_text(encoding="utf-8"))["id"])


def _fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - https site URL from the workflow
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("MD_PAGES_BUILD_MANIFEST")
    return payload


def wait_for_build(
    site_url: str,
    build_id: str,
    *,
    timeout: float = 300,
    interval: float = 10,
    fetch: Callable[[str], dict[str, Any]] = _fetch_json,
    clock: Clock = time,
) -> bool:
    url = site_url.rstrip("/") + "/" + MANIFEST
    deadline = clock.time() + timeout
    while True:
        try:
            if str(fetch(url).get("id")) == build_id:
                return True
        except (OSError, ValueError):
            pass
        if clock.time() + interval > deadline:
            return False
        clock.sleep(interval)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site_url", nargs="?")
    parser.add_argument("build_id", nargs="?")
    parser.add_argument("--local-id", type=Path, help="print the build id of a local static build and exit")
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--interval", type=float, default=10)
    args = parser.parse_args(argv)
    if args.local_id:
        print(local_build_id(args.local_id))
        return 0
    if not args.site_url or not args.build_id:
        parser.error("site_url and build_id are required")
    if wait_for_build(args.site_url, args.build_id, timeout=args.timeout, interval=args.interval):
        print(f"MD_PAGES_BUILD_LIVE:{args.build_id}")
        return 0
    print(f"MD_PAGES_BUILD_STALE:{args.build_id}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
