"""Tests for HTTP API client."""

from __future__ import annotations

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientError

from level_client.client import ApiError, Client

from .conftest import make_mock_response


class TestClientListLocks:
    """Tests for async_list_locks method."""

    @pytest.mark.asyncio
    async def test_success(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test successful list locks call."""
        mock_response = make_mock_response(
            json_data={"locks": [{"id": "101", "name": "Front Door"}]}
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        locks = await client.async_list_locks()
        
        assert len(locks) == 1
        assert locks[0]["id"] == "101"
        assert locks[0]["uuid"] == "101"  # Should add uuid from id
        
        # Verify request
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0] == ("GET", "https://api.example.com/v1/locks")
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_preserves_existing_uuid(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test list locks preserves existing uuid field."""
        mock_response = make_mock_response(
            json_data={"locks": [{"id": "101", "uuid": "201", "name": "Front Door"}]}
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        locks = await client.async_list_locks()
        
        assert locks[0]["uuid"] == "201"  # Should preserve existing uuid

    @pytest.mark.asyncio
    async def test_empty_list(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test list locks with empty response."""
        mock_response = make_mock_response(json_data={"locks": []})
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        locks = await client.async_list_locks()
        
        assert locks == []

    @pytest.mark.asyncio
    async def test_missing_locks_key(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test list locks when 'locks' key is missing."""
        mock_response = make_mock_response(json_data={})
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        locks = await client.async_list_locks()
        
        assert locks == []


class TestClientGetLockStatus:
    """Tests for async_get_lock_status method."""

    @pytest.mark.asyncio
    async def test_success(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test successful get lock status call."""
        mock_response = make_mock_response(
            json_data={"state": "locked", "battery": 80}
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        status = await client.async_get_lock_status("101")
        
        assert status["state"] == "locked"
        assert status["battery"] == 80
        
        # Verify request
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0] == ("GET", "https://api.example.com/v1/locks/101")


class TestClientLockUnlock:
    """Tests for async_lock and async_unlock methods."""

    @pytest.mark.asyncio
    async def test_lock_success(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test successful lock command."""
        mock_response = make_mock_response(
            content_type="text/plain", text_data="OK"
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        await client.async_lock("101")
        
        # Verify request
        call_args = mock_session.request.call_args
        assert call_args[0] == ("POST", "https://api.example.com/v1/locks/101/lock")

    @pytest.mark.asyncio
    async def test_unlock_success(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test successful unlock command."""
        mock_response = make_mock_response(
            content_type="text/plain", text_data="OK"
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        await client.async_unlock("101")
        
        # Verify request
        call_args = mock_session.request.call_args
        assert call_args[0] == ("POST", "https://api.example.com/v1/locks/101/unlock")


class TestClientErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_http_400_raises_api_error(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test HTTP 400 raises ApiError."""
        mock_response = make_mock_response(
            status=HTTPStatus.BAD_REQUEST, text_data="Bad Request"
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        
        with pytest.raises(ApiError, match="HTTP 400"):
            await client.async_list_locks()

    @pytest.mark.asyncio
    async def test_http_401_raises_api_error(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test HTTP 401 raises ApiError."""
        mock_response = make_mock_response(
            status=HTTPStatus.UNAUTHORIZED, text_data="Unauthorized"
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        
        with pytest.raises(ApiError, match="HTTP 401"):
            await client.async_list_locks()

    @pytest.mark.asyncio
    async def test_http_500_raises_api_error(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test HTTP 500 raises ApiError."""
        mock_response = make_mock_response(
            status=HTTPStatus.INTERNAL_SERVER_ERROR, text_data="Server Error"
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        
        with pytest.raises(ApiError, match="HTTP 500"):
            await client.async_list_locks()

    @pytest.mark.asyncio
    async def test_network_error_raises_api_error(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test network error raises ApiError."""
        mock_response = make_mock_response(raise_on_enter=ClientError())
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        
        with pytest.raises(ApiError, match="API error"):
            await client.async_list_locks()


class TestClientNormalized:
    """Tests for normalized methods."""

    @pytest.mark.asyncio
    async def test_list_locks_normalized_locked(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test list locks normalized includes is_locked field for locked state."""
        mock_response = make_mock_response(
            json_data={"locks": [{"id": "101", "state": "locked"}]}
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        locks = await client.async_list_locks_normalized()
        
        assert len(locks) == 1
        assert locks[0]["is_locked"] is True
        assert locks[0]["state"] == "locked"

    @pytest.mark.asyncio
    async def test_list_locks_normalized_unlocked(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test list locks normalized includes is_locked field for unlocked state."""
        mock_response = make_mock_response(
            json_data={"locks": [{"id": "101", "state": "unlocked"}]}
        )
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        locks = await client.async_list_locks_normalized()
        
        assert locks[0]["is_locked"] is False

    @pytest.mark.asyncio
    async def test_get_lock_status_bool_locked(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test get lock status bool returns True for locked."""
        mock_response = make_mock_response(json_data={"state": "locked"})
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        is_locked = await client.async_get_lock_status_bool("101")
        
        assert is_locked is True

    @pytest.mark.asyncio
    async def test_get_lock_status_bool_unlocked(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test get lock status bool returns False for unlocked."""
        mock_response = make_mock_response(json_data={"state": "unlocked"})
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        is_locked = await client.async_get_lock_status_bool("101")
        
        assert is_locked is False

    @pytest.mark.asyncio
    async def test_get_lock_status_bool_unknown(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test get lock status bool returns None for unknown state."""
        mock_response = make_mock_response(json_data={"state": "jammed"})
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com", mock_token_provider)
        is_locked = await client.async_get_lock_status_bool("102")
        
        assert is_locked is None


class TestClientBaseUrl:
    """Tests for base URL handling."""

    @pytest.mark.asyncio
    async def test_strips_trailing_slash(self, mock_session: MagicMock, mock_token_provider) -> None:
        """Test base URL trailing slash is stripped."""
        mock_response = make_mock_response(json_data={"locks": []})
        mock_session.request = MagicMock(return_value=mock_response)
        
        client = Client(mock_session, "https://api.example.com/", mock_token_provider)
        await client.async_list_locks()
        
        # Should not have double slash
        call_args = mock_session.request.call_args
        assert call_args[0][1] == "https://api.example.com/v1/locks"
