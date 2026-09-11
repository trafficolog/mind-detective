from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from scripts.local_execution_ast import PortableSourceError, validate_portable_source
from scripts.local_execution_manifest import load_contract_constants


_PUBLIC_EXPORTS = {
    "create_case",
    "apply_command",
    "build_checklist_proposal_json",
    "select_next_action_json",
}


@dataclass(frozen=True)
class _Signature:
    params: tuple[str, ...]
    defaults: tuple[ast.expr | None, ...]


def _json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


@lru_cache(maxsize=1)
def _casefold_table_json() -> str:
    mapping: dict[str, str] = {}
    for codepoint in range(0x110000):
        char = chr(codepoint)
        folded = char.casefold()
        if folded != char:
            mapping[str(codepoint)] = folded
    return json.dumps(mapping, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@lru_cache(maxsize=1)
def _whitespace_codepoints_json() -> str:
    values = [codepoint for codepoint in range(0x110000) if chr(codepoint).isspace()]
    return json.dumps(values, separators=(",", ":"))


def _prelude(contract_values: dict[str, object]) -> str:
    version = contract_values["LOCAL_EXECUTION_CONTRACT"]
    generator_version = contract_values["GENERATOR_VERSION"]
    command_types = contract_values["SUPPORTED_COMMAND_TYPES"]
    if not isinstance(version, str) or not isinstance(generator_version, str):
        raise ValueError("portable execution identity constants must be strings")
    if not isinstance(command_types, tuple) or not all(isinstance(item, str) for item in command_types):
        raise ValueError("SUPPORTED_COMMAND_TYPES must be a tuple of strings")
    commands_json = json.dumps(list(command_types), ensure_ascii=False, separators=(",", ":"))
    return f'''// GENERATED FILE — DO NOT EDIT
// contract: {version}
// generator: {generator_version}

export const LOCAL_EXECUTION_CONTRACT = {_json_string(version)}
export const GENERATOR_VERSION = {_json_string(generator_version)}
const SUPPORTED_COMMAND_TYPES = {commands_json}
const PY_CASEFOLD: Record<string, string> = {_casefold_table_json()}
const PY_WHITESPACE = new Set<number>({_whitespace_codepoints_json()})

export class PortableKernelError extends Error {{
  readonly code: string
  constructor(code: string, message: string) {{
    super(message)
    this.name = 'PortableKernelError'
    this.code = code
  }}
}}

function pyClone<T>(value: T): T {{
  return structuredClone(value)
}}

function pyCasefold(value: string): string {{
  let result = ''
  for (const char of value) {{
    const codepoint = char.codePointAt(0)
    if (codepoint === undefined) continue
    result += PY_CASEFOLD[String(codepoint)] ?? char
  }}
  return result
}}

function pySplitWhitespace(value: string): string[] {{
  const result: string[] = []
  let current = ''
  for (const char of value) {{
    const codepoint = char.codePointAt(0)
    if (codepoint !== undefined && PY_WHITESPACE.has(codepoint)) {{
      if (current.length > 0) {{
        result.push(current)
        current = ''
      }}
    }} else {{
      current += char
    }}
  }}
  if (current.length > 0) result.push(current)
  return result
}}

function pyCompareStrings(left: string, right: string): number {{
  const leftPoints = Array.from(left, (char) => char.codePointAt(0) ?? 0)
  const rightPoints = Array.from(right, (char) => char.codePointAt(0) ?? 0)
  const limit = Math.min(leftPoints.length, rightPoints.length)
  for (let index = 0; index < limit; index += 1) {{
    if (leftPoints[index] < rightPoints[index]) return -1
    if (leftPoints[index] > rightPoints[index]) return 1
  }}
  if (leftPoints.length < rightPoints.length) return -1
  if (leftPoints.length > rightPoints.length) return 1
  return 0
}}

function pyTruth(value: any): boolean {{
  if (value === null || value === undefined || value === false) return false
  if (typeof value === 'number') return value !== 0
  if (typeof value === 'string') return value.length > 0
  if (Array.isArray(value)) return value.length > 0
  if (value instanceof Set || value instanceof Map) return value.size > 0
  if (typeof value === 'object') return Object.keys(value).length > 0
  return true
}}

function pyEqual(left: any, right: any): boolean {{
  if (left === right) return true
  if (left === null || right === null || left === undefined || right === undefined) return false
  if (Array.isArray(left) && Array.isArray(right)) {{
    return left.length === right.length && left.every((value, index) => pyEqual(value, right[index]))
  }}
  if (left instanceof Set && right instanceof Set) {{
    if (left.size !== right.size) return false
    return Array.from(left).every((value) => pyContains(right, value))
  }}
  if (typeof left === 'object' && typeof right === 'object') {{
    const leftKeys = Object.keys(left)
    const rightKeys = Object.keys(right)
    if (leftKeys.length !== rightKeys.length) return false
    return leftKeys.every((key) => Object.prototype.hasOwnProperty.call(right, key) && pyEqual(left[key], right[key]))
  }}
  return false
}}

function pyContains(container: any, value: any): boolean {{
  if (container instanceof Set) return Array.from(container).some((item) => pyEqual(item, value))
  if (Array.isArray(container)) return container.some((item) => pyEqual(item, value))
  if (typeof container === 'string') return typeof value === 'string' && container.includes(value)
  if (container !== null && typeof container === 'object') return Object.prototype.hasOwnProperty.call(container, String(value))
  return false
}}

function pyGet(object: Record<string, any>, key: string, fallback: any = null): any {{
  return Object.prototype.hasOwnProperty.call(object, key) ? object[key] : fallback
}}

function pyItems(object: Record<string, any>): [string, any][] {{
  return Object.entries(object)
}}

function pySet(value: any): Set<any> {{
  if (value instanceof Set) return new Set(value)
  if (Array.isArray(value) || typeof value === 'string') return new Set(value)
  if (value !== null && typeof value === 'object') return new Set(Object.keys(value))
  return new Set(value)
}}

function pySetDifference(left: any, right: any): Set<any> {{
  const leftSet = pySet(left)
  const rightSet = pySet(right)
  return new Set(Array.from(leftSet).filter((value) => !pyContains(rightSet, value)))
}}

function pySorted(value: any): any[] {{
  return Array.from(value).sort((left, right) => {{
    if (typeof left === 'string' && typeof right === 'string') return pyCompareStrings(left, right)
    if (left < right) return -1
    if (left > right) return 1
    return 0
  }})
}}

function pyJoin(separator: string, values: any[]): string {{
  return values.map((value) => pyStr(value)).join(separator)
}}

function pyReplace(value: string, search: string, replacement: string): string {{
  if (search === '') {{
    const parts = Array.from(value)
    return replacement + parts.join(replacement) + replacement
  }}
  return value.split(search).join(replacement)
}}

function pyStr(value: any): string {{
  if (value === null) return 'None'
  if (value === true) return 'True'
  if (value === false) return 'False'
  return String(value)
}}

function pyIsDict(value: any): value is Record<string, any> {{
  return value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Set) && !(value instanceof Map)
}}

function pyIsFloat(value: any): boolean {{
  return typeof value === 'number' && !Number.isInteger(value)
}}

function pyOr<T>(left: T, right: () => T): T {{
  return pyTruth(left) ? left : right()
}}

function pyAnd<T>(left: T, right: () => T): T {{
  return pyTruth(left) ? right() : left
}}

function clone_json<T>(value: T): T {{ return pyClone(value) }}
function unicode_casefold(value: string): string {{ return pyCasefold(value) }}
function split_python_whitespace(value: string): string[] {{ return pySplitWhitespace(value) }}
function compare_python_strings(left: string, right: string): number {{ return pyCompareStrings(left, right) }}
function portable_error(code: string, message: string): never {{ throw new PortableKernelError(code, message) }}
'''


class _Emitter:
    def __init__(self, tree: ast.Module) -> None:
        self.tree = tree
        self.signatures = self._collect_signatures(tree)
        self._declared: list[set[str]] = [set()]
        self._indent = 0

    @staticmethod
    def _collect_signatures(tree: ast.Module) -> dict[str, _Signature]:
        signatures: dict[str, _Signature] = {}
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            positional = [arg.arg for arg in (*node.args.posonlyargs, *node.args.args)]
            defaults: list[ast.expr | None] = [None] * (len(positional) - len(node.args.defaults))
            defaults.extend(node.args.defaults)
            kwonly = [arg.arg for arg in node.args.kwonlyargs]
            defaults.extend(node.args.kw_defaults)
            signatures[node.name] = _Signature(tuple(positional + kwonly), tuple(defaults))
        return signatures

    def emit(self) -> str:
        lines: list[str] = []
        for node in self.tree.body:
            emitted = self._statement(node)
            if emitted:
                lines.extend(emitted)
        return "\n".join(lines).rstrip() + "\n"

    def _line(self, value: str) -> str:
        return "  " * self._indent + value

    def _statement(self, node: ast.stmt) -> list[str]:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return []
        if isinstance(node, ast.FunctionDef):
            return self._function(node)
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "multiple assignment targets are unsupported", "portable_kernel.py")
            return [self._line(self._assignment(node.targets[0], node.value))]
        if isinstance(node, ast.AnnAssign):
            if node.value is None:
                return []
            return [self._line(self._assignment(node.target, node.value))]
        if isinstance(node, ast.Return):
            return [self._line("return" if node.value is None else f"return {self._expr(node.value)}")]
        if isinstance(node, ast.Expr):
            return [self._line(self._expr(node.value))]
        if isinstance(node, ast.If):
            return self._if(node)
        if isinstance(node, ast.For):
            return self._for(node)
        if isinstance(node, ast.Break):
            return [self._line("break")]
        if isinstance(node, ast.Continue):
            return [self._line("continue")]
        raise PortableSourceError("MD_CODEGEN_EMIT", getattr(node, "lineno", 1), f"unsupported statement emission: {type(node).__name__}", "portable_kernel.py")

    def _function(self, node: ast.FunctionDef) -> list[str]:
        signature = self.signatures[node.name]
        params: list[str] = []
        for name, default in zip(signature.params, signature.defaults, strict=True):
            rendered = f"{name}: any"
            if default is not None:
                rendered += f" = {self._expr(default)}"
            params.append(rendered)
        prefix = "export " if node.name in _PUBLIC_EXPORTS else ""
        lines = [self._line(f"{prefix}function {node.name}({', '.join(params)}): any {{")]
        self._indent += 1
        self._declared.append(set(signature.params))
        for child in node.body:
            lines.extend(self._statement(child))
        self._declared.pop()
        self._indent -= 1
        lines.append(self._line("}"))
        lines.append("")
        return lines

    def _if(self, node: ast.If) -> list[str]:
        lines = [self._line(f"if (pyTruth({self._expr(node.test)})) {{")]
        self._indent += 1
        for child in node.body:
            lines.extend(self._statement(child))
        self._indent -= 1
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                nested = self._if(node.orelse[0])
                first = nested[0].lstrip()
                lines.append(self._line(f"}} else {first}"))
                lines.extend(nested[1:])
                return lines
            lines.append(self._line("} else {"))
            self._indent += 1
            for child in node.orelse:
                lines.extend(self._statement(child))
            self._indent -= 1
        lines.append(self._line("}"))
        return lines

    def _for(self, node: ast.For) -> list[str]:
        target = self._target(node.target, declaration=False)
        iterable = self._expr(node.iter)
        lines = [self._line(f"for (const {target} of {iterable}) {{")]
        self._indent += 1
        names = self._target_names(node.target)
        self._declared[-1].update(names)
        for child in node.body:
            lines.extend(self._statement(child))
        self._indent -= 1
        lines.append(self._line("}"))
        if node.orelse:
            raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "for/else is unsupported", "portable_kernel.py")
        return lines

    def _assignment(self, target: ast.expr, value: ast.expr) -> str:
        rendered_value = self._expr(value)
        if isinstance(target, ast.Name):
            if target.id not in self._declared[-1]:
                self._declared[-1].add(target.id)
                return f"let {target.id} = {rendered_value}"
            return f"{target.id} = {rendered_value}"
        return f"{self._target(target, declaration=False)} = {rendered_value}"

    def _target(self, node: ast.expr, *, declaration: bool) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, (ast.Tuple, ast.List)):
            return "[" + ", ".join(self._target(item, declaration=declaration) for item in node.elts) + "]"
        if isinstance(node, ast.Subscript):
            return f"{self._expr(node.value)}[{self._expr(node.slice)}]"
        if isinstance(node, ast.Attribute):
            return f"{self._expr(node.value)}.{node.attr}"
        raise PortableSourceError("MD_CODEGEN_EMIT", getattr(node, "lineno", 1), f"unsupported assignment target: {type(node).__name__}", "portable_kernel.py")

    def _target_names(self, node: ast.expr) -> set[str]:
        if isinstance(node, ast.Name):
            return {node.id}
        if isinstance(node, (ast.Tuple, ast.List)):
            names: set[str] = set()
            for item in node.elts:
                names.update(self._target_names(item))
            return names
        return set()

    def _expr(self, node: ast.expr) -> str:
        if isinstance(node, ast.Constant):
            if node.value is None:
                return "null"
            if node.value is True:
                return "true"
            if node.value is False:
                return "false"
            if isinstance(node.value, str):
                return _json_string(node.value)
            if isinstance(node.value, int):
                return str(node.value)
            raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, f"unsupported constant: {node.value!r}", "portable_kernel.py")
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.List):
            return "[" + ", ".join(self._expr(item) for item in node.elts) + "]"
        if isinstance(node, ast.Tuple):
            return "[" + ", ".join(self._expr(item) for item in node.elts) + "]"
        if isinstance(node, ast.Set):
            return "new Set([" + ", ".join(self._expr(item) for item in node.elts) + "])"
        if isinstance(node, ast.Dict):
            pairs: list[str] = []
            for key, value in zip(node.keys, node.values, strict=True):
                if key is None:
                    raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "dict unpacking is unsupported", "portable_kernel.py")
                rendered_key = self._expr(key)
                pairs.append(f"[{rendered_key}]: {self._expr(value)}")
            return "{" + ", ".join(pairs) + "}"
        if isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Slice):
                return self._slice(node.value, node.slice)
            return f"{self._expr(node.value)}[{self._expr(node.slice)}]"
        if isinstance(node, ast.Attribute):
            return f"{self._expr(node.value)}.{node.attr}"
        if isinstance(node, ast.Call):
            return self._call(node)
        if isinstance(node, ast.JoinedStr):
            return self._joined_string(node)
        if isinstance(node, ast.Compare):
            return self._compare(node)
        if isinstance(node, ast.BoolOp):
            return self._bool_op(node)
        if isinstance(node, ast.BinOp):
            return self._bin_op(node)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return f"!pyTruth({self._expr(node.operand)})"
            if isinstance(node.op, ast.USub):
                return f"-({self._expr(node.operand)})"
        raise PortableSourceError("MD_CODEGEN_EMIT", getattr(node, "lineno", 1), f"unsupported expression emission: {type(node).__name__}", "portable_kernel.py")

    def _slice(self, value: ast.expr, node: ast.Slice) -> str:
        base = self._expr(value)
        step = self._literal_int(node.step)
        lower = "" if node.lower is None else self._expr(node.lower)
        upper = "" if node.upper is None else self._expr(node.upper)
        if step == -1 and node.lower is None and node.upper is None:
            return f"{base}.slice().reverse()"
        if step not in (None, 1):
            raise PortableSourceError("MD_CODEGEN_EMIT", getattr(node, "lineno", 1), "only normal slices and [::-1] are supported", "portable_kernel.py")
        if node.upper is None:
            return f"{base}.slice({lower or '0'})"
        return f"{base}.slice({lower or '0'}, {upper})"

    @staticmethod
    def _literal_int(node: ast.expr | None) -> int | None:
        if node is None:
            return None
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, int):
            return -node.operand.value
        return None

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
                raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, f"keywords unsupported for call: {name}", "portable_kernel.py")
            return f"{name}({', '.join(args)})"
        if isinstance(node.func, ast.Attribute):
            receiver = self._expr(node.func.value)
            method = node.func.attr
            args = [self._expr(arg) for arg in node.args]
            if node.keywords:
                raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, f"keywords unsupported for method: {method}", "portable_kernel.py")
            if method == "get":
                fallback = args[1] if len(args) > 1 else "null"
                return f"pyGet({receiver}, {args[0]}, {fallback})"
            if method == "items":
                return f"pyItems({receiver})"
            if method == "append":
                return f"{receiver}.push({args[0]})"
            if method == "add":
                return f"{receiver}.add({args[0]})"
            if method == "join":
                return f"pyJoin({receiver}, {args[0]})"
            if method == "replace":
                return f"pyReplace({receiver}, {args[0]}, {args[1]})"
            if method == "upper":
                return f"{receiver}.toUpperCase()"
            raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, f"unsupported method emission: {method}", "portable_kernel.py")
        raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "dynamic call emission is unsupported", "portable_kernel.py")

    def _ordered_call_arguments(self, node: ast.Call, signature: _Signature) -> list[str]:
        supplied: dict[str, str] = {}
        for index, arg in enumerate(node.args):
            if index >= len(signature.params):
                raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "too many positional arguments", "portable_kernel.py")
            supplied[signature.params[index]] = self._expr(arg)
        for keyword in node.keywords:
            if keyword.arg is None:
                raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "keyword unpacking is unsupported", "portable_kernel.py")
            supplied[keyword.arg] = self._expr(keyword.value)
        last_index = max((signature.params.index(name) for name in supplied), default=-1)
        result: list[str] = []
        for index in range(last_index + 1):
            name = signature.params[index]
            result.append(supplied.get(name, "undefined"))
        return result

    def _isinstance(self, node: ast.Call) -> str:
        if len(node.args) != 2:
            raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "isinstance requires two arguments", "portable_kernel.py")
        value = self._expr(node.args[0])
        type_node = node.args[1]
        if isinstance(type_node, ast.Name):
            return self._single_isinstance(value, type_node.id, node.lineno)
        if isinstance(type_node, ast.Tuple):
            checks = [self._single_isinstance(value, self._type_name(item, node.lineno), node.lineno) for item in type_node.elts]
            return "(" + " || ".join(checks) + ")"
        raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "unsupported isinstance type", "portable_kernel.py")

    @staticmethod
    def _type_name(node: ast.expr, line: int) -> str:
        if isinstance(node, ast.Name):
            return node.id
        raise PortableSourceError("MD_CODEGEN_EMIT", line, "unsupported isinstance tuple member", "portable_kernel.py")

    @staticmethod
    def _single_isinstance(value: str, type_name: str, line: int) -> str:
        mapping = {
            "str": f"typeof {value} === 'string'",
            "dict": f"pyIsDict({value})",
            "Mapping": f"pyIsDict({value})",
            "list": f"Array.isArray({value})",
            "tuple": f"Array.isArray({value})",
            "float": f"pyIsFloat({value})",
            "bool": f"typeof {value} === 'boolean'",
            "int": f"typeof {value} === 'number' && Number.isInteger({value})",
        }
        rendered = mapping.get(type_name)
        if rendered is None:
            raise PortableSourceError("MD_CODEGEN_EMIT", line, f"unsupported isinstance target: {type_name}", "portable_kernel.py")
        return f"({rendered})"

    def _joined_string(self, node: ast.JoinedStr) -> str:
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                escaped = value.value.replace("`", "\\`").replace("${", "\\${")
                parts.append(escaped)
            elif isinstance(value, ast.FormattedValue):
                parts.append("${pyStr(" + self._expr(value.value) + ")}")
            else:
                raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, "unsupported f-string part", "portable_kernel.py")
        return "`" + "".join(parts) + "`"

    def _compare(self, node: ast.Compare) -> str:
        left = node.left
        pieces: list[str] = []
        for op, right in zip(node.ops, node.comparators, strict=True):
            pieces.append(self._compare_pair(left, op, right))
            left = right
        return "(" + " && ".join(pieces) + ")"

    def _compare_pair(self, left: ast.expr, op: ast.cmpop, right: ast.expr) -> str:
        lvalue = self._expr(left)
        rvalue = self._expr(right)
        if isinstance(op, ast.Eq):
            return f"pyEqual({lvalue}, {rvalue})"
        if isinstance(op, ast.NotEq):
            return f"!pyEqual({lvalue}, {rvalue})"
        if isinstance(op, ast.In):
            return f"pyContains({rvalue}, {lvalue})"
        if isinstance(op, ast.NotIn):
            return f"!pyContains({rvalue}, {lvalue})"
        if isinstance(op, ast.Is):
            return f"({lvalue} === {rvalue})"
        if isinstance(op, ast.IsNot):
            return f"({lvalue} !== {rvalue})"
        if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
            operator = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}[type(op)]
            return f"({lvalue} {operator} {rvalue})"
        raise PortableSourceError("MD_CODEGEN_EMIT", getattr(op, "lineno", 1), f"unsupported comparison: {type(op).__name__}", "portable_kernel.py")

    def _bool_op(self, node: ast.BoolOp) -> str:
        values = [self._expr(value) for value in node.values]
        if not values:
            return "false"
        result = values[-1]
        helper = "pyAnd" if isinstance(node.op, ast.And) else "pyOr"
        for value in reversed(values[:-1]):
            result = f"{helper}({value}, () => {result})"
        return result

    def _bin_op(self, node: ast.BinOp) -> str:
        left = self._expr(node.left)
        right = self._expr(node.right)
        if isinstance(node.op, ast.Sub):
            return f"pySetDifference({left}, {right})"
        if isinstance(node.op, ast.Add):
            return f"({left} + {right})"
        if isinstance(node.op, ast.BitOr):
            return f"({left} | {right})"
        raise PortableSourceError("MD_CODEGEN_EMIT", node.lineno, f"unsupported binary operator: {type(node.op).__name__}", "portable_kernel.py")


def generate_typescript(kernel_path: Path, contract_path: Path) -> str:
    validate_portable_source(kernel_path, profile="kernel")
    intrinsics_path = kernel_path.with_name("portable_intrinsics.py")
    validate_portable_source(intrinsics_path, profile="intrinsics")
    contract_values = load_contract_constants(contract_path)
    source = kernel_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(kernel_path))
    return _prelude(contract_values) + "\n" + _Emitter(tree).emit()
