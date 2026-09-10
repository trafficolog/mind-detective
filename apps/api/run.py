from __future__ import annotations

import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parent
REPO_ROOT = API_ROOT.parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins/mind-detective"

for path in (API_ROOT, PLUGIN_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import uvicorn  # noqa: E402


if __name__ == "__main__":
    uvicorn.run("mind_detective_api.app:app", host="127.0.0.1", port=8000, reload=False)
