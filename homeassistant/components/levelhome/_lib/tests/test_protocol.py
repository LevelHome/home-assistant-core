"""Tests for protocol utilities."""

from __future__ import annotations

import pytest

from level_client.protocol import (
    coerce_is_locked,
    extract_device_name,
    extract_device_uuid,
    normalize_device,
    parse_bolt_state,
)


# --- coerce_is_locked tests ---


def test_coerce_is_locked_locked() -> None:
    """Test coerce_is_locked returns True for locked states."""
    assert coerce_is_locked("locked") is True
    assert coerce_is_locked("Locked") is True
    assert coerce_is_locked("LOCKED") is True
    assert coerce_is_locked("lock") is True
    assert coerce_is_locked("secure") is True
    assert coerce_is_locked(True) is True


def test_coerce_is_locked_unlocked() -> None:
    """Test coerce_is_locked returns False for unlocked states."""
    assert coerce_is_locked("unlocked") is False
    assert coerce_is_locked("Unlocked") is False
    assert coerce_is_locked("UNLOCKED") is False
    assert coerce_is_locked("unlock") is False
    assert coerce_is_locked("insecure") is False
    assert coerce_is_locked(False) is False


def test_coerce_is_locked_transitional() -> None:
    """Test coerce_is_locked returns None for transitional states."""
    assert coerce_is_locked("locking") is None
    assert coerce_is_locked("Locking") is None
    assert coerce_is_locked("unlocking") is None
    assert coerce_is_locked("Unlocking") is None


def test_coerce_is_locked_none() -> None:
    """Test coerce_is_locked returns None for None input."""
    assert coerce_is_locked(None) is None


def test_coerce_is_locked_unknown() -> None:
    """Test coerce_is_locked returns None for unknown states."""
    assert coerce_is_locked("unknown") is None
    assert coerce_is_locked("") is None
    assert coerce_is_locked(123) is None
    assert coerce_is_locked([]) is None


# --- extract_device_uuid tests ---


def test_extract_device_uuid_device_uuid_key() -> None:
    """Test extraction with device_uuid key."""
    assert extract_device_uuid({"device_uuid": "123"}) == "123"


def test_extract_device_uuid_uuid_key() -> None:
    """Test extraction with uuid key."""
    assert extract_device_uuid({"uuid": "456"}) == "456"


def test_extract_device_uuid_uppercase_key() -> None:
    """Test extraction with UUID key."""
    assert extract_device_uuid({"UUID": "789"}) == "789"


def test_extract_device_uuid_id_key() -> None:
    """Test extraction with id key as fallback."""
    assert extract_device_uuid({"id": "999"}) == "999"


def test_extract_device_uuid_priority() -> None:
    """Test device_uuid takes priority over other keys."""
    data = {"device_uuid": "100", "uuid": "200", "id": "300"}
    assert extract_device_uuid(data) == "100"


def test_extract_device_uuid_missing() -> None:
    """Test extraction returns None when no UUID key found."""
    assert extract_device_uuid({}) is None
    assert extract_device_uuid({"name": "test"}) is None


# --- extract_device_name tests ---


def test_extract_device_name_name_key() -> None:
    """Test extraction with name key."""
    assert extract_device_name({"name": "Front Door"}) == "Front Door"


def test_extract_device_name_device_name_key() -> None:
    """Test extraction with device_name key."""
    assert extract_device_name({"device_name": "Back Door"}) == "Back Door"


def test_extract_device_name_priority() -> None:
    """Test name takes priority over device_name."""
    data = {"name": "Primary", "device_name": "Secondary"}
    assert extract_device_name(data) == "Primary"


def test_extract_device_name_with_fallback() -> None:
    """Test extraction uses fallback when no name found."""
    assert extract_device_name({}, fallback="123") == "123"


def test_extract_device_name_default_fallback() -> None:
    """Test extraction uses default fallback when no name or fallback."""
    assert extract_device_name({}) == "Level Lock"


# --- parse_bolt_state tests ---


def test_parse_bolt_state_locked() -> None:
    """Test parsing locked bolt state."""
    is_locked, state = parse_bolt_state({"bolt_state": "Locked"})
    assert is_locked is True
    assert state == "Locked"


def test_parse_bolt_state_unlocked() -> None:
    """Test parsing unlocked bolt state."""
    is_locked, state = parse_bolt_state({"bolt_state": "Unlocked"})
    assert is_locked is False
    assert state == "Unlocked"


def test_parse_bolt_state_none_input() -> None:
    """Test parsing with None input."""
    is_locked, state = parse_bolt_state(None)
    assert is_locked is None
    assert state is None


def test_parse_bolt_state_missing_key() -> None:
    """Test parsing when bolt_state key is missing."""
    is_locked, state = parse_bolt_state({})
    assert is_locked is None
    assert state is None


def test_parse_bolt_state_none_value() -> None:
    """Test parsing when bolt_state value is None."""
    is_locked, state = parse_bolt_state({"bolt_state": None})
    assert is_locked is None
    assert state is None


# --- normalize_device tests ---


def test_normalize_device_full_data() -> None:
    """Test normalizing device with full data."""
    device_data = {"device_uuid": "123", "name": "Front Door"}
    device_state = {"bolt_state": "Locked"}
    
    device = normalize_device(device_data, device_state)
    
    assert device.device_uuid == "123"
    assert device.name == "Front Door"
    assert device.is_locked is True
    assert device.state == "Locked"


def test_normalize_device_minimal_data() -> None:
    """Test normalizing device with minimal data."""
    device_data = {"device_uuid": "456"}
    
    device = normalize_device(device_data)
    
    assert device.device_uuid == "456"
    assert device.name == "456"  # Falls back to UUID
    assert device.is_locked is None
    assert device.state is None


def test_normalize_device_no_uuid() -> None:
    """Test normalizing device with no UUID uses 'unknown'."""
    device_data = {"name": "Test Lock"}
    
    device = normalize_device(device_data)
    
    assert device.device_uuid == "unknown"
    assert device.name == "Test Lock"


def test_normalize_device_unlocked_state() -> None:
    """Test normalizing device with unlocked state."""
    device_data = {"device_uuid": "789", "name": "Back Door"}
    device_state = {"bolt_state": "Unlocked"}
    
    device = normalize_device(device_data, device_state)
    
    assert device.device_uuid == "789"
    assert device.name == "Back Door"
    assert device.is_locked is False
    assert device.state == "Unlocked"
