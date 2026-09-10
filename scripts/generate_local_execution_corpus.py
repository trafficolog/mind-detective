from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.local_execution_manifest import load_contract_constants, sha256_prefixed

SEED = 303001


def _oracle_vectors(root: Path) -> list[dict[str, object]]:
    plugin_root = root / "plugins/mind-detective"
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(plugin_root) if not existing else str(plugin_root) + os.pathsep + existing
    env["PYTHONHASHSEED"] = "0"
    process = subprocess.run(
        [sys.executable, "-m", "scripts.conformance_vectors"],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError("MD_LOCAL_CONFORMANCE_ORACLE: " + process.stderr.strip())
    parsed = json.loads(process.stdout)
    if not isinstance(parsed, list) or not all(isinstance(item, dict) for item in parsed):
        raise RuntimeError("MD_LOCAL_CONFORMANCE_ORACLE: oracle returned invalid vector list")
    return parsed


def render_corpus(root: Path) -> tuple[bytes, bytes]:
    vectors = _oracle_vectors(root)
    vectors_bytes = (
        json.dumps(vectors, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")

    contract_path = root / "plugins/mind-detective/scripts/portable_contract.py"
    kernel_path = root / "plugins/mind-detective/scripts/portable_kernel.py"
    values = load_contract_constants(contract_path)
    version = values["LOCAL_EXECUTION_CONTRACT"]
    generator_version = values["GENERATOR_VERSION"]
    if not isinstance(version, str) or not isinstance(generator_version, str):
        raise RuntimeError("MD_LOCAL_CONFORMANCE_ORACLE: invalid contract identity")

    manifest = {
        "contract_version": version,
        "generator_version": generator_version,
        "kernel_sha256": sha256_prefixed(kernel_path.read_bytes()),
        "seed": SEED,
        "vector_count": len(vectors),
        "vectors_sha256": sha256_prefixed(vectors_bytes),
    }
    manifest_bytes = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    return vectors_bytes, manifest_bytes


def write_corpus(root: Path) -> None:
    vectors, manifest = render_corpus(root)
    destination = root / "conformance/local-execution/v1"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "vectors.json").write_bytes(vectors)
    (destination / "manifest.json").write_bytes(manifest)


def main() -> None:
    write_corpus(Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
