"""Library-shared protocol helpers for Level Lock.

Pure helper module to avoid circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def coerce_is_locked(state: Any) -> bool | None:
    """Convert vendor state to boolean locked status or None for unknown.

    Transitional states (e.g., "locking"/"unlocking") return None.
    """

    if state is None:
        return None
    if isinstance(state, str):
        lowered = state.lower()
        if lowered in ("locked", "lock", "secure"):
            return True
        if lowered in ("unlocked", "unlock", "insecure"):
            return False
        if lowered in ("locking", "unlocking"):
            return None
    if isinstance(state, bool):
        return state
    return None


@dataclass(slots=True)
class NormalizedDevice:
    """Normalized device data from the Level API."""

    device_uuid: str
    name: str
    is_locked: bool | None
    state: str | None


def extract_device_uuid(device_data: dict[str, Any]) -> str | None:
    """Extract device UUID from raw device data dict.

    Handles various key names used by the API.
    """
    return device_data.get("device_uuid") or device_data.get("uuid") or device_data.get("UUID") or device_data.get("id")


def extract_device_name(device_data: dict[str, Any], fallback: str | None = None) -> str:
    """Extract device name from raw device data dict with fallback."""
    name = device_data.get("name") or device_data.get("device_name")
    if name:
        return str(name)
    if fallback:
        return fallback
    return "Level Lock"


def parse_bolt_state(device_state: dict[str, Any] | None) -> tuple[bool | None, str | None]:
    """Parse device state dict to (is_locked, state_string).

    Returns:
        Tuple of (is_locked boolean or None, state string or None)
    """
    if device_state is None:
        return None, None

    bolt_state = device_state.get("bolt_state")
    if bolt_state is None:
        return None, None

    state_str = str(bolt_state)
    is_locked = coerce_is_locked(state_str)
    return is_locked, state_str


def normalize_device(
    device_data: dict[str, Any],
    device_state: dict[str, Any] | None = None,
) -> NormalizedDevice:
    """Normalize raw device data into a structured NormalizedDevice.

    Args:
        device_data: Raw device dict from list_devices response
        device_state: Optional device state dict from get_device_state response

    Returns:
        NormalizedDevice with extracted/normalized fields
    """
    device_uuid = extract_device_uuid(device_data) or "unknown"
    name = extract_device_name(device_data, fallback=device_uuid)
    is_locked, state = parse_bolt_state(device_state)

    return NormalizedDevice(
        device_uuid=device_uuid,
        name=name,
        is_locked=is_locked,
        state=state,
    )
