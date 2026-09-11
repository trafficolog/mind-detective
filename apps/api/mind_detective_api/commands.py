from __future__ import annotations

from .contracts import CommandEnvelope
from .core_bridge import validate_or_migrate_case_payload

from scripts.portable_intrinsics import PortableKernelError
from scripts.portable_kernel import apply_command


class CommandError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def execute_command(
    case_payload: dict[str, object],
    envelope: CommandEnvelope,
) -> dict[str, object]:
    canonical_payload = validate_or_migrate_case_payload(case_payload)
    command_payload: dict[str, object] = envelope.model_dump(mode="python")
    try:
        return apply_command(canonical_payload, command_payload)
    except PortableKernelError as exc:
        raise CommandError(exc.code, str(exc)) from exc
