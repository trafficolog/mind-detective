from __future__ import annotations

import ast
from pathlib import Path
from typing import Literal

Profile = Literal["kernel", "intrinsics"]


class PortableSourceError(ValueError):
    def __init__(self, code: str, line: int, detail: str, source_name: str) -> None:
        super().__init__(f"{source_name}:{line}: {detail}")
        self.code = code
        self.line = line
        self.detail = detail
        self.source_name = source_name


_COMMON_ALLOWED_NODES: tuple[type[ast.AST], ...] = (
    ast.Module,
    ast.ImportFrom,
    ast.alias,
    ast.Assign,
    ast.AnnAssign,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Return,
    ast.If,
    ast.For,
    ast.Break,
    ast.Continue,
    ast.Expr,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Dict,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Subscript,
    ast.Slice,
    ast.Attribute,
    ast.Call,
    ast.keyword,
    ast.JoinedStr,
    ast.FormattedValue,
    ast.Compare,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.BitOr,
    ast.USub,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)

_KERNEL_IMPORTS: dict[tuple[int, str], frozenset[str]] = {
    (0, "__future__"): frozenset({"annotations"}),
    (0, "collections.abc"): frozenset({"Mapping"}),
    (1, "portable_contract"): frozenset({"SUPPORTED_COMMAND_TYPES"}),
    (1, "portable_intrinsics"): frozenset(
        {
            "PortableKernelError",
            "clone_json",
            "compare_python_strings",
            "portable_error",
            "split_python_whitespace",
            "unicode_casefold",
        }
    ),
}

_INTRINSIC_IMPORTS: dict[tuple[int, str], frozenset[str]] = {
    (0, "__future__"): frozenset({"annotations"}),
    (0, "copy"): frozenset({"deepcopy"}),
    (0, "typing"): frozenset({"NoReturn", "TypeVar"}),
}

_KERNEL_BUILTIN_CALLS = frozenset(
    {"bool", "frozenset", "isinstance", "list", "set", "sorted", "str"}
)
_KERNEL_INTRINSIC_CALLS = frozenset(
    {
        "clone_json",
        "compare_python_strings",
        "portable_error",
        "split_python_whitespace",
        "unicode_casefold",
    }
)
_KERNEL_METHOD_CALLS = frozenset({"add", "append", "get", "items", "join", "replace", "upper"})

_INTRINSIC_NAME_CALLS = frozenset(
    {"PortableKernelError", "TypeVar", "deepcopy", "super"}
)
_INTRINSIC_METHOD_CALLS = frozenset({"__init__", "casefold", "split"})


class _Validator(ast.NodeVisitor):
    def __init__(self, *, profile: Profile, source_name: str) -> None:
        self.profile = profile
        self.source_name = source_name
        self.local_functions: set[str] = set()

    def fail(self, code: str, node: ast.AST, detail: str) -> None:
        raise PortableSourceError(code, max(getattr(node, "lineno", 1), 1), detail, self.source_name)

    def validate(self, tree: ast.Module) -> None:
        self.local_functions = {
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        self.visit(tree)

    def generic_visit(self, node: ast.AST) -> None:
        allowed = _COMMON_ALLOWED_NODES
        if self.profile == "intrinsics":
            allowed = allowed + (ast.ClassDef, ast.Raise)
        if not isinstance(node, allowed):
            self.fail("MD_CODEGEN_NODE", node, f"unsupported AST node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.fail("MD_CODEGEN_ASYNC", node, "async functions are forbidden")

    def visit_Await(self, node: ast.Await) -> None:
        self.fail("MD_CODEGEN_ASYNC", node, "await is forbidden")

    def visit_Yield(self, node: ast.Yield) -> None:
        self.fail("MD_CODEGEN_ASYNC", node, "yield is forbidden")

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self.fail("MD_CODEGEN_ASYNC", node, "yield from is forbidden")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if self.profile != "intrinsics" or node.name != "PortableKernelError":
            self.fail("MD_CODEGEN_CLASS", node, "classes are forbidden in portable kernel source")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.fail("MD_CODEGEN_IMPORT", node, "plain imports are forbidden")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        allowed_imports = _KERNEL_IMPORTS if self.profile == "kernel" else _INTRINSIC_IMPORTS
        allowed_names = allowed_imports.get((node.level, module))
        names = {alias.name for alias in node.names}
        if allowed_names is None or not names.issubset(allowed_names):
            self.fail("MD_CODEGEN_IMPORT", node, f"import is not allowlisted: {module}")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, float):
            self.fail("MD_CODEGEN_FLOAT", node, "floating-point constants are forbidden")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if self.profile == "kernel":
                allowed = self.local_functions | _KERNEL_BUILTIN_CALLS | _KERNEL_INTRINSIC_CALLS
            else:
                allowed = self.local_functions | _INTRINSIC_NAME_CALLS
            if name not in allowed:
                self.fail("MD_CODEGEN_CALL", node, f"call is not allowlisted: {name}")
        elif isinstance(node.func, ast.Attribute):
            method = node.func.attr
            allowed_methods = (
                _KERNEL_METHOD_CALLS if self.profile == "kernel" else _INTRINSIC_METHOD_CALLS
            )
            if method not in allowed_methods:
                self.fail("MD_CODEGEN_CALL", node, f"method call is not allowlisted: {method}")
        else:
            self.fail("MD_CODEGEN_CALL", node, "dynamic calls are forbidden")
        self.generic_visit(node)


def validate_source_text(
    source: str,
    *,
    profile: Profile,
    source_name: str = "<portable-source>",
) -> None:
    try:
        tree = ast.parse(source, filename=source_name)
    except SyntaxError as exc:
        raise PortableSourceError(
            "MD_CODEGEN_SYNTAX",
            max(exc.lineno or 1, 1),
            exc.msg,
            source_name,
        ) from exc
    _Validator(profile=profile, source_name=source_name).validate(tree)


def validate_portable_source(path: Path, *, profile: Profile) -> None:
    validate_source_text(path.read_text(encoding="utf-8"), profile=profile, source_name=str(path))
