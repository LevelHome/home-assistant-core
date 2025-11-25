"""WebSocket push client for Level Lock using ws-partner-server protocol.

This module provides a manager that maintains a single WebSocket connection
to the ws-partner-server for all devices on an account.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any, Literal

from aiohttp import ClientError, ClientSession, ClientWebSocketResponse, WSMsgType

from level_client.generated.level_api.models import (
    DevicesRemovedMessage,
    DeviceStateChangedMessage,
    DevicesUpdatedMessage,
    GetDeviceStateMessage,
    GetDeviceStateReplyMessage,
    ListDevicesMessage,
    ListDevicesReplyMessage,
    LockMessage,
    LockReplyMessage,
    PongMessage,
    UnlockMessage,
    UnlockReplyMessage,
)
from level_client.generated.level_api.types import Unset
from level_client.protocol import (
    NormalizedDevice,
    extract_device_uuid,
    normalize_device,
)

LOGGER = logging.getLogger(__name__)

TokenProvider = Callable[[], Awaitable[str]]

WsCommandType = Literal["lock", "unlock"]


class LevelWebsocketManager:
    """Manage WebSocket connection to ws-partner-server."""

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        get_token: TokenProvider,
        on_state_update: Callable[[str, bool | None, dict[str, Any] | None], Awaitable[None]],
    ) -> None:
        self._get_token = get_token
        self._base_url = base_url.rstrip("/")
        self._on_state_update = on_state_update
        self._session: ClientSession = session
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None
        self._ws: ClientWebSocketResponse | None = None
        self._send_lock = asyncio.Lock()
        self._device_uuid_map: dict[str, str] = {}
        self._devices_list: list[dict[str, Any]] = []
        self._list_devices_event = asyncio.Event()
        self._pending_state_requests: dict[str, tuple[asyncio.Event, dict[str, Any] | None]] = {}

    async def async_start(self, lock_ids: list[str] | None = None) -> None:
        """Start WebSocket connection."""
        LOGGER.info("Starting WebSocket connection")
        if self._task is None or self._task.done():
            self._stop_event.clear()
            self._list_devices_event.clear()
            self._task = asyncio.create_task(self._run_connection())
            LOGGER.info("WebSocket connection task created, waiting 0.5s for connection")
            await asyncio.sleep(0.5)
            LOGGER.info(
                "Initial wait complete, WebSocket connected: %s",
                self._ws is not None and not (self._ws.closed if self._ws else True),
            )
        await self._fetch_device_list()

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Get list of devices via WebSocket."""
        LOGGER.info("Requesting device list via WebSocket")
        self._list_devices_event.clear()
        await self._fetch_device_list()
        try:
            await asyncio.wait_for(self._list_devices_event.wait(), timeout=10.0)
            LOGGER.info("Received device list with %d devices", len(self._devices_list))
        except TimeoutError:
            LOGGER.warning("Timeout waiting for device list response")
        return self._devices_list

    async def async_get_devices_normalized(self) -> list[NormalizedDevice]:
        """Get list of devices with normalized data and current state.

        This is a convenience method that fetches device list and state,
        then returns normalized device objects ready for use.

        Returns:
            List of NormalizedDevice objects with device_uuid, name, is_locked, state
        """
        devices_data = await self.async_get_devices()
        normalized: list[NormalizedDevice] = []

        for device_data in devices_data:
            device_uuid = extract_device_uuid(device_data)
            if not device_uuid:
                LOGGER.warning("Skipping device with no UUID: %s", device_data)
                continue

            # Fetch current state for the device
            device_state = await self.async_get_device_state(device_uuid)

            # Normalize the device data
            device = normalize_device(device_data, device_state)
            normalized.append(device)
            LOGGER.debug(
                "Normalized device: uuid=%s, name=%s, is_locked=%s, state=%s",
                device.device_uuid,
                device.name,
                device.is_locked,
                device.state,
            )

        LOGGER.info("Normalized %d devices", len(normalized))
        return normalized

    async def async_stop(self) -> None:
        """Stop WebSocket connection and background task."""
        self._stop_event.set()
        if self._ws is not None and not self._ws.closed:
            with suppress(Exception):
                await self._ws.close()
        if self._task is not None:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    def register_device_uuid(self, lock_id: str, device_uuid: str) -> None:
        """Register mapping from lock_id to device_uuid."""
        self._device_uuid_map[lock_id] = device_uuid

    async def _safe_send_json(self, message_dict: dict[str, Any], timeout: float = 5.0) -> None:
        """Send a JSON message with timeout protection.

        Raises:
            ConnectionError: If WebSocket is not connected or closed
            asyncio.TimeoutError: If send operation times out (connection likely stale)
        """
        async with self._send_lock:
            if self._ws is None or self._ws.closed:
                raise ConnectionError("WebSocket not connected")

            try:
                await asyncio.wait_for(self._ws.send_json(message_dict), timeout=timeout)
            except asyncio.TimeoutError:
                LOGGER.warning("Timeout sending WebSocket message, marking connection stale")
                self._ws = None
                raise
            except (ClientError, OSError) as err:
                LOGGER.warning("Error sending WebSocket message: %s", err)
                self._ws = None
                raise ConnectionError(str(err)) from err

    async def async_send_command(self, lock_id: str, command: WsCommandType) -> None:
        """Send a lock/unlock command via WebSocket."""
        LOGGER.info("Sending %s command for lock %s", command, lock_id)
        device_uuid = self._device_uuid_map.get(lock_id)
        if device_uuid is None:
            raise ValueError(f"Device UUID not found for lock_id {lock_id}")
        if command == "lock":
            message = LockMessage(type_="lock", device_uuid=device_uuid)
        else:
            message = UnlockMessage(type_="unlock", device_uuid=device_uuid)
        LOGGER.info("Sending WebSocket message: %s", message.to_dict())
        await self._safe_send_json(message.to_dict())

    async def async_get_device_state(self, device_uuid: str) -> dict[str, Any] | None:
        """Get device state via WebSocket."""
        LOGGER.info("Requesting device state for %s", device_uuid)
        event = asyncio.Event()
        self._pending_state_requests[device_uuid] = (event, None)
        try:
            LOGGER.info("Sending get_device_state request for %s", device_uuid)
            message = GetDeviceStateMessage(type_="get_device_state", device_uuid=device_uuid)
            await self._safe_send_json(message.to_dict())
            LOGGER.info("Waiting for device state response for %s", device_uuid)
            await asyncio.wait_for(event.wait(), timeout=5.0)
            _, result = self._pending_state_requests.get(device_uuid, (None, None))
            LOGGER.info("Received device state for %s: %s", device_uuid, result)
            return result
        except (TimeoutError, ConnectionError):
            LOGGER.warning("Timeout or connection error getting state for device %s", device_uuid)
            return None
        finally:
            self._pending_state_requests.pop(device_uuid, None)

    async def _fetch_device_list(self) -> None:
        """Fetch device list via WebSocket list_devices message."""
        LOGGER.info("Fetching device list")
        try:
            LOGGER.info("Sending list_devices request")
            message = ListDevicesMessage(type_="list_devices")
            await self._safe_send_json(message.to_dict())
        except ConnectionError:
            LOGGER.warning("Cannot fetch device list - WebSocket not connected")
            return

    async def _run_connection(self) -> None:
        """Background task to keep WebSocket connected."""
        backoff_seconds = 1.0
        max_backoff = 30.0
        url = f"{self._base_url}/v1/ws"
        while not self._stop_event.is_set():
            try:
                token = await self._get_token()
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                }
                LOGGER.debug("Connecting WebSocket to %s", url)
                ws = await self._session.ws_connect(url, headers=headers, heartbeat=30)
                self._ws = ws
                backoff_seconds = 1.0
                LOGGER.info("WebSocket connected")
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        await self._handle_text_message(msg.data)
                    elif msg.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                        break
            except asyncio.CancelledError:
                break
            except ClientError as err:
                LOGGER.warning("WebSocket error: %s", err)
            except Exception:
                LOGGER.exception("Unexpected WebSocket error")
            finally:
                if self._ws is not None and not self._ws.closed:
                    with suppress(Exception):
                        await self._ws.close()
                self._ws = None
            if self._stop_event.is_set():
                break
            sleep_time = backoff_seconds + random.uniform(0, 0.5)
            LOGGER.debug("Reconnecting WebSocket in %.1fs", sleep_time)
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=sleep_time)
                break
            except TimeoutError:
                pass
            backoff_seconds = min(max_backoff, backoff_seconds * 2.0)

    async def _handle_text_message(self, data: str) -> None:
        """Handle a JSON text message from the server."""
        try:
            payload = json.loads(data)
        except Exception:
            LOGGER.debug("Non-JSON message: %s", data)
            return
        msg_type: str | None = payload.get("type")
        LOGGER.info("Received WebSocket message type: %s", msg_type)

        if msg_type == "list_devices_reply":
            try:
                msg = ListDevicesReplyMessage.from_dict(payload)
                # Convert DeviceListItem objects to dicts for backward compatibility
                devices = [device.to_dict() for device in msg.devices]
                self._devices_list = devices
                for device in msg.devices:
                    device_uuid = device.device_uuid
                    if device_uuid:
                        self._device_uuid_map[device_uuid] = device_uuid
                LOGGER.info("Received device list with %d devices", len(devices))
                self._list_devices_event.set()
            except Exception as e:
                LOGGER.warning("Failed to parse list_devices_reply: %s", e)
            return

        if msg_type == "lock_reply":
            try:
                msg = LockReplyMessage.from_dict(payload)
                LOGGER.info(
                    "Received lock_reply: success=%s, device=%s, error=%s",
                    msg.success,
                    msg.device_uuid,
                    msg.error if not isinstance(msg.error, Unset) else None,
                )
                if not msg.success and not isinstance(msg.error, Unset) and msg.error:
                    LOGGER.warning("Lock command failed for device %s: %s", msg.device_uuid, msg.error)
                    return
                if msg.success and msg.device_uuid:
                    state_payload = {"state": "locked", "device_uuid": msg.device_uuid}
                    LOGGER.info("Updating state for device %s to locked", msg.device_uuid)
                    await self._on_state_update(msg.device_uuid, True, state_payload)
            except Exception as e:
                LOGGER.warning("Failed to parse lock_reply: %s", e)
            return

        if msg_type == "unlock_reply":
            try:
                msg = UnlockReplyMessage.from_dict(payload)
                LOGGER.info(
                    "Received unlock_reply: success=%s, device=%s, error=%s",
                    msg.success,
                    msg.device_uuid,
                    msg.error if not isinstance(msg.error, Unset) else None,
                )
                if not msg.success and not isinstance(msg.error, Unset) and msg.error:
                    LOGGER.warning("Unlock command failed for device %s: %s", msg.device_uuid, msg.error)
                    return
                if msg.success and msg.device_uuid:
                    state_payload = {"state": "unlocked", "device_uuid": msg.device_uuid}
                    LOGGER.info("Updating state for device %s to unlocked", msg.device_uuid)
                    await self._on_state_update(msg.device_uuid, False, state_payload)
            except Exception as e:
                LOGGER.warning("Failed to parse unlock_reply: %s", e)
            return

        if msg_type == "pong":
            try:
                PongMessage.from_dict(payload)  # Validate but don't need to do anything
            except Exception as e:
                LOGGER.warning("Failed to parse pong: %s", e)
            return

        if msg_type == "get_device_state_reply":
            try:
                msg = GetDeviceStateReplyMessage.from_dict(payload)
                LOGGER.info("Received device state reply for %s", msg.device_uuid)
                if msg.device_uuid and msg.device_uuid in self._pending_state_requests:
                    event, _ = self._pending_state_requests[msg.device_uuid]
                    # Convert DeviceStateInfo to dict for backward compatibility
                    device_state_dict = msg.device_state.to_dict() if not isinstance(msg.device_state, Unset) else None
                    self._pending_state_requests[msg.device_uuid] = (event, device_state_dict)
                    event.set()
                    LOGGER.info("Device state event set for %s", msg.device_uuid)
                else:
                    LOGGER.warning("Received state reply for unknown or expired request: %s", msg.device_uuid)
            except Exception as e:
                LOGGER.warning("Failed to parse get_device_state_reply: %s", e)
            return

        if msg_type == "device_state_changed":
            try:
                msg = DeviceStateChangedMessage.from_dict(payload)
                LOGGER.info(
                    "Received device state change for %s (%s)",
                    msg.device_uuid,
                    msg.device_name,
                )
                if msg.device_uuid and not isinstance(msg.device_state, Unset):
                    device_state = msg.device_state
                    bolt_state = device_state.bolt_state if not isinstance(device_state.bolt_state, Unset) else None
                    is_locked = None
                    state_str = None
                    if bolt_state == "Locked":
                        is_locked = True
                        state_str = "locked"
                    elif bolt_state == "Unlocked":
                        is_locked = False
                        state_str = "unlocked"
                    state_payload = {
                        "state": state_str,
                        "device_uuid": msg.device_uuid,
                        "device_name": msg.device_name,
                        "bolt_state": bolt_state,
                        "battery_level": (
                            device_state.battery_level if not isinstance(device_state.battery_level, Unset) else None
                        ),
                        "reachable": (
                            device_state.reachable if not isinstance(device_state.reachable, Unset) else None
                        ),
                    }
                    LOGGER.info(
                        "Processing state change for device %s: bolt_state=%s, is_locked=%s, state=%s",
                        msg.device_uuid,
                        bolt_state,
                        is_locked,
                        state_str,
                    )
                    await self._on_state_update(msg.device_uuid, is_locked, state_payload)
            except Exception as e:
                LOGGER.warning("Failed to parse device_state_changed: %s", e)
            return

        if msg_type == "devices_updated":
            try:
                msg = DevicesUpdatedMessage.from_dict(payload)
                LOGGER.info("Received devices_updated with %d devices", len(msg.devices))
                # Convert DeviceUpdateInfo objects to dicts for backward compatibility
                updated_devices = [device.to_dict() for device in msg.devices]
                # Update device list - merge with existing or replace based on device_uuid
                device_dict = {device["device_uuid"]: device for device in self._devices_list}
                for device in updated_devices:
                    device_uuid = device.get("device_uuid")
                    if device_uuid:
                        device_dict[device_uuid] = device
                        self._device_uuid_map[device_uuid] = device_uuid
                self._devices_list = list(device_dict.values())
                LOGGER.info("Updated device list, now contains %d devices", len(self._devices_list))
            except Exception as e:
                LOGGER.warning("Failed to parse devices_updated: %s", e)
            return

        if msg_type == "devices_removed":
            try:
                msg = DevicesRemovedMessage.from_dict(payload)
                LOGGER.info("Received devices_removed with %d device UUIDs", len(msg.device_uuids))
                # Remove devices from device list
                removed_uuids = set(msg.device_uuids)
                self._devices_list = [
                    device for device in self._devices_list if device.get("device_uuid") not in removed_uuids
                ]
                # Remove from device UUID map
                for device_uuid in removed_uuids:
                    self._device_uuid_map.pop(device_uuid, None)
                LOGGER.info(
                    "Removed %d devices, device list now contains %d devices",
                    len(removed_uuids),
                    len(self._devices_list),
                )
            except Exception as e:
                LOGGER.warning("Failed to parse devices_removed: %s", e)
            return

        LOGGER.info("Unhandled message type: %s, payload: %s", msg_type, payload)
