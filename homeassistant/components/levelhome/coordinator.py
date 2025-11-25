"""Coordinator and device mapping for Level Lock devices."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from level_client import LevelWebsocketManager

LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL: timedelta | None = None  # Use push updates; no periodic polling


@dataclass(slots=True)
class LevelLockDevice:
    """Representation of a Level lock device."""

    lock_id: str
    uuid: str
    name: str
    is_locked: bool | None
    state: str | None = None


class LevelLocksCoordinator(DataUpdateCoordinator[dict[str, LevelLockDevice]]):
    """Coordinator to fetch all locks for the account."""

    def __init__(
        self, hass: HomeAssistant, ws_manager: LevelWebsocketManager, *, config_entry: ConfigEntry
    ) -> None:
        """Initialize the Level locks coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            name="Level Lock devices",
            update_interval=SCAN_INTERVAL,
            config_entry=config_entry,
        )
        self._ws_manager = ws_manager

    async def _async_update_data(self) -> dict[str, LevelLockDevice]:
        """Fetch devices from WebSocket and convert to HA device objects."""
        try:
            normalized_devices = await self._ws_manager.async_get_devices_normalized()
        except Exception as err:
            raise UpdateFailed(str(err)) from err
        
        # Convert library NormalizedDevice to HA LevelLockDevice
        result: dict[str, LevelLockDevice] = {}
        for device in normalized_devices:
            ha_device = LevelLockDevice(
                lock_id=device.device_uuid,
                uuid=device.device_uuid,
                name=device.name,
                is_locked=device.is_locked,
                state=device.state,
            )
            result[ha_device.lock_id] = ha_device
            self._ws_manager.register_device_uuid(ha_device.lock_id, ha_device.uuid)
        
        return result

    async def async_stop_push(self) -> None:
        """Stop push connections."""
        await self._ws_manager.async_stop()

    async def async_handle_push_update(
        self, lock_id: str, is_locked: bool | None, payload: dict[str, Any] | None
    ) -> None:
        """Handle a push state update from the WebSocket."""
        current = dict(self.data or {})
        device = current.get(lock_id)
        if device is None:
            device_name = payload.get("device_name") if payload else None
            if device_name:
                for d in current.values():
                    if d.name == device_name:
                        device = d
                        LOGGER.info("Matched device by name: %s -> %s", lock_id, device.lock_id)
                        break
            if device is None:
                LOGGER.info("Creating new device entry from push update: %s (%s)", lock_id, device_name)
                device = LevelLockDevice(
                    lock_id=lock_id,
                    uuid=lock_id,
                    name=device_name or lock_id,
                    is_locked=is_locked,
                    state=payload.get("state") if payload else None,
                )
                current[lock_id] = device
                self._ws_manager.register_device_uuid(device.lock_id, device.uuid)

        if is_locked is not None:
            device.is_locked = is_locked
        if payload is not None and "state" in payload:
            state = payload.get("state")
            device.state = str(state) if state is not None else None
        LOGGER.info("Updated device %s: is_locked=%s, state=%s", device.lock_id, device.is_locked, device.state)
        self.async_set_updated_data(current)

    async def async_send_command(self, lock_id: str, command: str) -> None:
        """Send a command via WebSocket."""
        if command in ("lock", "unlock"):
            try:
                await self._ws_manager.async_send_command(
                    lock_id,
                    command,  # type: ignore[arg-type]
                )
            except Exception as err:
                raise UpdateFailed(f"Command failed: {err}") from err
