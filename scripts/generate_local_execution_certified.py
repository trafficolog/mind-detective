from __future__ import annotations

import ast
from pathlib import Path

from scripts.generate_local_execution import _Emitter, _PUBLIC_EXPORTS, _prelude
from scripts.local_execution_ast import PortableSourceError, validate_portable_source
from scripts.local_execution_manifest import load_contract_constants

# Python identifiers can be legal while the same spelling is reserved in JS/TS.
# `$` cannot occur in a Python identifier, so the mapping is deterministic and collision-free.
_JS_RESERVED = frozenset(
    {
        "await",
        "break",
        "case",
        "catch",
        "class",
        "const",
        "continue",
        "debugger",
        "default",
        "delete",
        "do",
        "else",
        "enum",
        "export",
        "extends",
        "false",
        "finally",
        "for",
        "function",
        "if",
        "implements",
        "import",
        "in",
        "instanceof",
        "interface",
        "let",
        "new",
        "null",
        "package",
        "private",
        "protected",
        "public",
        "return",
        "static",
        "super",
        "switch",
        "this",
        "throw",
        "true",
        "try",
        "typeof",
        "var",
        "void",
        "while",
        "with",
        "yield",
    }
)


def _js_name(name: str) -> str:
    return f"{name}$" if name in _JS_RESERVED else name


class _LocalCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802 - ast visitor contract
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names.add(node.id)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802 - ast visitor contract
        # Nested functions are outside the portable subset. Do not leak their locals.
        return


class CertifiedEmitter(_Emitter):
    """Emitter that preserves Python function-local scope and avoids JS/TS reserved names."""

    @staticmethod
    def _function_locals(node: ast.FunctionDef, params: tuple[str, ...]) -> list[str]:
        collector = _LocalCollector()
        for child in node.body:
            collector.visit(child)
        collector.names.difference_update(params)
        return sorted(collector.names)

    def _function(self, node: ast.FunctionDef) -> list[str]:
        signature = self.signatures[node.name]
        params: list[str] = []
        for name, default in zip(signature.params, signature.defaults, strict=True):
            rendered = f"{_js_name(name)}: any"
            if default is not None:
                rendered += f" = {self._expr(default)}"
            params.append(rendered)

        prefix = "export " if node.name in _PUBLIC_EXPORTS else ""
        lines = [self._line(f"{prefix}function {_js_name(node.name)}({', '.join(params)}): any {{")]
        self._indent += 1

        locals_ = self._function_locals(node, signature.params)
        self._declared.append(set(signature.params) | set(locals_))
        if locals_:
            rendered_locals = ", ".join(_js_name(name) for name in locals_)
            lines.append(self._line(f"let {rendered_locals}: any"))

        for child in node.body:
            lines.extend(self._statement(child))

        self._declared.pop()
        self._indent -= 1
        lines.append(self._line("}"))
        lines.append("")
        return lines

    def _assignment(self, target: ast.expr, value: ast.expr) -> str:
        rendered_value = self._expr(value)
        if isinstance(target, ast.Name):
            rendered_name = _js_name(target.id)
            if len(self._declared) == 1 and target.id not in self._declared[-1]:
                self._declared[-1].add(target.id)
                return f"let {rendered_name} = {rendered_value}"
            return f"{rendered_name} = {rendered_value}"
        return f"{self._target(target, declaration=False)} = {rendered_value}"

    def _for(self, node: ast.For) -> list[str]:
        target = self._target(node.target, declaration=False)
        iterable = self._expr(node.iter)
        # Python loop targets are function-scoped. They were predeclared by _function().
        lines = [self._line(f"for ({target} of {iterable}) {{")]
        self._indent += 1
        for child in node.body:
            lines.extend(self._statement(child))
        self._indent -= 1
        lines.append(self._line("}"))
        if node.orelse:
            raise PortableSourceError(
                "MD_CODEGEN_EMIT",
                node.lineno,
                "for/else is unsupported",
                "portable_kernel.py",
            )
        return lines

    def _target(self, node: ast.expr, *, declaration: bool) -> str:
        if isinstance(node, ast.Name):
            return _js_name(node.id)
        return super()._target(node, declaration=declaration)

    def _expr(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return _js_name(node.id)
        return super()._expr(node)

    def _call(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            name = node.func.id
            args = [self._expr(arg) for arg in node.args]
            if name == "frozenset":
                return f"new Set({args[0] if args else '[]'})"
            if name == "set":
                return f"pySet({args[0] if args else '[]'})"
            if name == "sorted":
                return f"pySorted({args[0]})"
            if name == "list":
                return f"Array.from({args[0]})"
            if name == "str":
                return f"pyStr({args[0]})"
            if name == "bool":
                return f"pyTruth({args[0]})"
            if name == "isinstance":
                return self._isinstance(node)
            signature = self.signatures.get(name)
            if signature is not None and node.keywords:
                args = self._ordered_call_arguments(node, signature)
            elif node.keywords:
                raise PortableSourceError(
                    "MD_CODEGEN_EMIT",
                    node.lineno,
                    f"keywords unsupported for call: {name}",
                    "portable_kernel.py",
                )
            return f"{_js_name(name)}({', '.join(args)})"
        return super()._call(node)


def generate_certified_typescript(kernel_path: Path, contract_path: Path) -> str:
    validate_portable_source(kernel_path, profile="kernel")
    intrinsics_path = kernel_path.with_name("portable_intrinsics.py")
    validate_portable_source(intrinsics_path, profile="intrinsics")
    contract_values = load_contract_constants(contract_path)
    source = kernel_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(kernel_path))
    return _prelude(contract_values) + "\n" + CertifiedEmitter(tree).emit()


__all__ = ["CertifiedEmitter", "generate_certified_typescript"]
