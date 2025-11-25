"""Shared fixtures for level_client tests."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientSession


@pytest.fixture
def mock_session() -> MagicMock:
    """Mock aiohttp ClientSession."""
    return MagicMock(spec=ClientSession)


@pytest.fixture
async def mock_token_provider() -> Callable[[], Awaitable[str]]:
    """Mock token provider function."""
    async def provider() -> str:
        return "test-token"
    return provider


@pytest.fixture
def mock_on_state_update() -> AsyncMock:
    """Mock state update callback."""
    return AsyncMock()


def make_mock_response(
    *,
    status: HTTPStatus = HTTPStatus.OK,
    json_data: dict[str, Any] | None = None,
    text_data: str = "",
    content_type: str = "application/json",
    raise_on_enter: Exception | None = None,
) -> MagicMock:
    """Create a mock aiohttp response with async context manager support.
    
    Args:
        status: HTTP status code
        json_data: JSON response data (if content_type is application/json)
        text_data: Text response data
        content_type: Response content type
        raise_on_enter: Exception to raise when entering context manager
    
    Returns:
        MagicMock configured as an async context manager response
    """
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.content_type = content_type
    mock_response.json = AsyncMock(return_value=json_data)
    mock_response.text = AsyncMock(return_value=text_data)
    
    if raise_on_enter:
        mock_response.__aenter__ = AsyncMock(side_effect=raise_on_enter)
    else:
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    
    return mock_response
