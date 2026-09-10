from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_local_execution import generate_typescript
from scripts.local_execution_manifest import build_execution_metadata

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "plugins/mind-detective/scripts/portable_kernel.py"
CONTRACT = ROOT / "plugins/mind-detective/scripts/portable_contract.py"
GENERATED_DIR = ROOT / "apps/web/app/generated"
GENERATED_TS = GENERATED_DIR / "localExecution.ts"
GENERATED_META = GENERATED_DIR / "localExecution.meta.json"


def render_artifacts() -> tuple[str, str]:
    generated = generate_typescript(KERNEL, CONTRACT)
    metadata = build_execution_metadata(
        kernel_bytes=KERNEL.read_bytes(),
        generated_bytes=generated.encode("utf-8"),
        contract_path=CONTRACT,
    )
    metadata_text = json.dumps(
        metadata,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    return generated, metadata_text


def write_artifacts() -> None:
    generated, metadata_text = render_artifacts()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_TS.write_text(generated, encoding="utf-8")
    GENERATED_META.write_text(metadata_text, encoding="utf-8")


if __name__ == "__main__":
    write_artifacts()
