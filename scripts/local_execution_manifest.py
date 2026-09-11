from __future__ import annotations

import ast
import hashlib
from pathlib import Path


def sha256_prefixed(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_contract_constants(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: dict[str, object] = {}
    wanted = {
        "LOCAL_EXECUTION_CONTRACT",
        "GENERATOR_VERSION",
        "SUPPORTED_CASE_SCHEMAS",
        "SUPPORTED_COMMAND_TYPES",
    }
    for node in tree.body:
        name: str | None = None
        value_node: ast.expr | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            value_node = node.value
        if name in wanted and value_node is not None:
            values[name] = ast.literal_eval(value_node)
    missing = wanted - set(values)
    if missing:
        raise ValueError("missing portable contract constants: " + ",".join(sorted(missing)))
    return values


def build_execution_metadata(
    *,
    kernel_bytes: bytes,
    generated_bytes: bytes,
    contract_path: Path,
) -> dict[str, object]:
    values = load_contract_constants(contract_path)
    case_schemas = values["SUPPORTED_CASE_SCHEMAS"]
    if not isinstance(case_schemas, tuple) or not all(isinstance(value, str) for value in case_schemas):
        raise ValueError("SUPPORTED_CASE_SCHEMAS must be a tuple of strings")
    version = values["LOCAL_EXECUTION_CONTRACT"]
    generator_version = values["GENERATOR_VERSION"]
    if not isinstance(version, str) or not isinstance(generator_version, str):
        raise ValueError("portable execution identity constants must be strings")
    return {
        "version": version,
        "kernel_sha256": sha256_prefixed(kernel_bytes),
        "generated_sha256": sha256_prefixed(generated_bytes),
        "generator_version": generator_version,
        "case_schemas": list(case_schemas),
    }
