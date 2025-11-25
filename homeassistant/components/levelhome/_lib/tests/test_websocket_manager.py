"""Tests for WebSocket manager."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientError

from level_client.ws import LevelWebsocketManager


class TestWebsocketManagerBasics:
    """Basic WebSocket manager tests."""

    @pytest.mark.asyncio
    async def test_register_device_uuid(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test registering device UUID mapping."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        manager.register_device_uuid("100", "200")
        assert manager._device_uuid_map["100"] == "200"

    @pytest.mark.asyncio
    async def test_start_creates_task(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test start creates background connection task."""
        mock_ws = _make_mock_websocket()
        mock_session.ws_connect = AsyncMock(return_value=mock_ws)
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        await manager.async_start()
        assert manager._task is not None
        assert not manager._task.done()
        
        await manager.async_stop()

    @pytest.mark.asyncio
    async def test_stop_sets_event_and_cancels_task(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test stop sets event and cancels task."""
        mock_ws = _make_mock_websocket()
        mock_session.ws_connect = AsyncMock(return_value=mock_ws)
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        await manager.async_start()
        await manager.async_stop()
        
        assert manager._stop_event.is_set()


class TestSafeSendJson:
    """Tests for _safe_send_json method."""

    @pytest.mark.asyncio
    async def test_sends_message_when_connected(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test sends message when websocket is connected."""
        mock_ws = _make_mock_websocket()
        mock_session.ws_connect = AsyncMock(return_value=mock_ws)
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        
        await manager._safe_send_json({"type": "test"})
        
        mock_ws.send_json.assert_called_once_with({"type": "test"})

    @pytest.mark.asyncio
    async def test_raises_when_not_connected(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test raises ConnectionError when not connected."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        with pytest.raises(ConnectionError, match="WebSocket not connected"):
            await manager._safe_send_json({"type": "test"})

    @pytest.mark.asyncio
    async def test_raises_when_closed(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test raises ConnectionError when websocket is closed."""
        mock_ws = _make_mock_websocket()
        mock_ws.closed = True
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        
        with pytest.raises(ConnectionError, match="WebSocket not connected"):
            await manager._safe_send_json({"type": "test"})

    @pytest.mark.asyncio
    async def test_timeout_marks_connection_stale(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test timeout marks connection as stale."""
        mock_ws = _make_mock_websocket()
        mock_ws.send_json = AsyncMock(side_effect=asyncio.TimeoutError())
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        
        with pytest.raises(asyncio.TimeoutError):
            await manager._safe_send_json({"type": "test"}, timeout=0.1)
        
        assert manager._ws is None  # Should be marked stale

    @pytest.mark.asyncio
    async def test_client_error_marks_connection_stale(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test ClientError marks connection as stale."""
        mock_ws = _make_mock_websocket()
        mock_ws.send_json = AsyncMock(side_effect=ClientError())
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        
        with pytest.raises(ConnectionError):
            await manager._safe_send_json({"type": "test"})
        
        assert manager._ws is None


class TestSendCommand:
    """Tests for async_send_command method."""

    @pytest.mark.asyncio
    async def test_lock_command(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test sending lock command."""
        mock_ws = _make_mock_websocket()
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        manager.register_device_uuid("100", "200")
        
        await manager.async_send_command("100", "lock")
        
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "lock"
        assert call_args["device_uuid"] == "200"

    @pytest.mark.asyncio
    async def test_unlock_command(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test sending unlock command."""
        mock_ws = _make_mock_websocket()
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        manager.register_device_uuid("100", "200")
        
        await manager.async_send_command("100", "unlock")
        
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "unlock"
        assert call_args["device_uuid"] == "200"

    @pytest.mark.asyncio
    async def test_raises_for_unknown_lock_id(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test raises ValueError for unregistered lock ID."""
        mock_ws = _make_mock_websocket()
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        
        with pytest.raises(ValueError, match="Device UUID not found"):
            await manager.async_send_command("999", "lock")

    @pytest.mark.asyncio
    async def test_raises_when_not_connected(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test raises ConnectionError when not connected."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager.register_device_uuid("100", "200")
        
        with pytest.raises(ConnectionError, match="WebSocket not connected"):
            await manager.async_send_command("100", "lock")


class TestHandleTextMessage:
    """Tests for _handle_text_message method."""

    @pytest.mark.asyncio
    async def test_list_devices_reply(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling list_devices_reply message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {
            "type": "list_devices_reply",
            "devices": [
                {
                    "device_uuid": "101",
                    "name": "Front Door",
                    "serial_number": "SN001",
                    "product": "Level Lock",
                    "location_uuid": "500",
                },
                {
                    "device_uuid": "102",
                    "name": "Back Door",
                    "serial_number": "SN002",
                    "product": "Level Lock",
                    "location_uuid": "500",
                },
            ]
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        assert len(manager._devices_list) == 2
        assert manager._device_uuid_map["101"] == "101"
        assert manager._device_uuid_map["102"] == "102"
        assert manager._list_devices_event.is_set()

    @pytest.mark.asyncio
    async def test_lock_reply_success(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling successful lock_reply message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {
            "type": "lock_reply",
            "success": True,
            "device_uuid": "101",
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        mock_on_state_update.assert_called_once()
        call_args = mock_on_state_update.call_args[0]
        assert call_args[0] == "101"
        assert call_args[1] is True  # is_locked

    @pytest.mark.asyncio
    async def test_lock_reply_failure(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling failed lock_reply message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {
            "type": "lock_reply",
            "success": False,
            "device_uuid": "101",
            "error": "Lock jammed",
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        mock_on_state_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_unlock_reply_success(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling successful unlock_reply message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {
            "type": "unlock_reply",
            "success": True,
            "device_uuid": "101",
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        mock_on_state_update.assert_called_once()
        call_args = mock_on_state_update.call_args[0]
        assert call_args[0] == "101"
        assert call_args[1] is False  # is_locked

    @pytest.mark.asyncio
    async def test_get_device_state_reply(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling get_device_state_reply message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        # Set up a pending request
        event = asyncio.Event()
        manager._pending_state_requests["101"] = (event, None)
        
        payload = {
            "type": "get_device_state_reply",
            "device_uuid": "101",
            "device_state": {"bolt_state": "Locked", "battery_level": 85},
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        assert event.is_set()
        _, state = manager._pending_state_requests["101"]
        assert state["bolt_state"] == "Locked"

    @pytest.mark.asyncio
    async def test_device_state_changed_locked(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling device_state_changed message with locked state."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {
            "type": "device_state_changed",
            "device_uuid": "101",
            "device_name": "Front Door",
            "location_uuid": "500",
            "location_name": "Home",
            "device_state": {
                "bolt_state": "Locked",
                "battery_level": 80,
                "reachable": True,
            },
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        mock_on_state_update.assert_called_once()
        call_args = mock_on_state_update.call_args[0]
        assert call_args[0] == "101"
        assert call_args[1] is True  # is_locked
        assert call_args[2]["bolt_state"] == "Locked"

    @pytest.mark.asyncio
    async def test_device_state_changed_unlocked(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling device_state_changed message with unlocked state."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {
            "type": "device_state_changed",
            "device_uuid": "101",
            "device_name": "Front Door",
            "location_uuid": "500",
            "location_name": "Home",
            "device_state": {"bolt_state": "Unlocked"},
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        call_args = mock_on_state_update.call_args[0]
        assert call_args[1] is False  # is_locked

    @pytest.mark.asyncio
    async def test_devices_updated(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling devices_updated message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        # Pre-populate with existing device
        manager._devices_list = [{"device_uuid": "101", "device_name": "Old Name"}]
        
        payload = {
            "type": "devices_updated",
            "devices": [
                {
                    "device_uuid": "101",
                    "device_name": "New Name",
                    "serial_number": "SN001",
                    "product": "Level Lock",
                    "location_uuid": "500",
                    "location_name": "Home",
                }
            ],
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        assert len(manager._devices_list) == 1
        assert manager._devices_list[0]["device_name"] == "New Name"
        assert manager._device_uuid_map["101"] == "101"

    @pytest.mark.asyncio
    async def test_devices_removed(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling devices_removed message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        # Pre-populate with devices
        manager._devices_list = [
            {"device_uuid": "101", "name": "Door 1"},
            {"device_uuid": "102", "name": "Door 2"},
        ]
        manager._device_uuid_map = {"101": "101", "102": "102"}
        
        payload = {
            "type": "devices_removed",
            "device_uuids": ["101"],
        }
        
        await manager._handle_text_message(json.dumps(payload))
        
        assert len(manager._devices_list) == 1
        assert manager._devices_list[0]["device_uuid"] == "102"
        assert "101" not in manager._device_uuid_map

    @pytest.mark.asyncio
    async def test_pong_message(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling pong message (no-op)."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {"type": "pong"}
        
        # Should not raise
        await manager._handle_text_message(json.dumps(payload))

    @pytest.mark.asyncio
    async def test_invalid_json(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling invalid JSON message."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        # Should not raise, just log
        await manager._handle_text_message("not valid json")

    @pytest.mark.asyncio
    async def test_unknown_message_type(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test handling unknown message type."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        payload = {"type": "unknown_type", "data": "test"}
        
        # Should not raise, just log
        await manager._handle_text_message(json.dumps(payload))


class TestGetDevices:
    """Tests for async_get_devices and async_get_devices_normalized."""

    @pytest.mark.asyncio
    async def test_get_devices_returns_cached_list(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test get devices returns cached device list."""
        mock_ws = _make_mock_websocket()
        mock_session.ws_connect = AsyncMock(return_value=mock_ws)
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        # Pre-populate devices and set event
        manager._devices_list = [{"device_uuid": "101"}]
        manager._list_devices_event.set()
        manager._ws = mock_ws
        
        devices = await manager.async_get_devices()
        
        assert len(devices) == 1
        assert devices[0]["device_uuid"] == "101"

    @pytest.mark.asyncio
    async def test_get_devices_empty_when_no_response(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test get devices returns empty list when no devices received."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        # Simulate scenario where event was set but no devices populated
        # (e.g., empty response from server)
        manager._list_devices_event.set()
        manager._devices_list = []
        
        devices = await manager.async_get_devices()
        
        assert devices == []


class TestGetDeviceState:
    """Tests for async_get_device_state."""

    @pytest.mark.asyncio
    async def test_returns_none_when_not_connected(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test returns None when not connected."""
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        
        state = await manager.async_get_device_state("101")
        
        assert state is None

    @pytest.mark.asyncio
    async def test_returns_state_on_reply(
        self, mock_session: MagicMock, mock_token_provider, mock_on_state_update: AsyncMock
    ) -> None:
        """Test returns state when reply received."""
        mock_ws = _make_mock_websocket()
        
        manager = LevelWebsocketManager(
            mock_session, "https://api.example.com", mock_token_provider, mock_on_state_update
        )
        manager._ws = mock_ws
        
        # Simulate reply coming in
        async def simulate_reply():
            await asyncio.sleep(0.01)
            reply = {
                "type": "get_device_state_reply",
                "device_uuid": "101",
                "device_state": {"bolt_state": "Locked"},
            }
            await manager._handle_text_message(json.dumps(reply))
        
        asyncio.create_task(simulate_reply())
        state = await manager.async_get_device_state("101")
        
        assert state is not None
        assert state["bolt_state"] == "Locked"


# --- Helper functions ---

def _make_mock_websocket() -> MagicMock:
    """Create a mock WebSocket connection."""
    async def empty_async_iter():
        if False:
            yield
        return
    
    mock_ws = MagicMock()
    mock_ws.closed = False
    mock_ws.__aiter__ = lambda: empty_async_iter()
    mock_ws.send_json = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws
