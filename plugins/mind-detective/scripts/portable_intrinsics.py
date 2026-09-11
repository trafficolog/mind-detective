from __future__ import annotations

from copy import deepcopy
from typing import NoReturn, TypeVar

_T = TypeVar("_T")


class PortableKernelError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def clone_json(value: _T) -> _T:
    return deepcopy(value)


def unicode_casefold(value: str) -> str:
    return value.casefold()


def split_python_whitespace(value: str) -> list[str]:
    return value.split()


def compare_python_strings(left: str, right: str) -> int:
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def portable_error(code: str, message: str) -> NoReturn:
    raise PortableKernelError(code, message)
