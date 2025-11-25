"""Tests for the Level Lock config flow."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from aiohttp import ClientError
import pytest

from homeassistant import config_entries
from homeassistant.components.levelhome.config_flow import OAuth2FlowHandler
from homeassistant.components.levelhome.const import (
    CONF_PARTNER_BASE_URL,
    DEFAULT_PARTNER_BASE_URL,
    DEVICE_CODE_INITIATE_PATH,
    DOMAIN,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker


@pytest.mark.usefixtures("mock_oauth_patches", "mock_oauth_responses")
async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test the full happy path of the device code OAuth2 config flow."""
    # Begin flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Submit empty input to use defaults for base URLs
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    # Next step should prompt for verification (device code flow)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "verify"

    # Submit empty input to proceed to polling (user verifies on mobile app)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Level Lock"
    # Entry data contains the token and implementation domain
    assert result["data"]["auth_implementation"] == DOMAIN
    token = result["data"]["token"]
    assert token["access_token"] == "at"
    assert token["refresh_token"] == "rt"
    assert token["token_type"].lower() == "bearer"
    assert isinstance(token["expires_in"], int)
    assert "expires_at" in token
    # Options store selected base URLs
    assert result["options"][CONF_PARTNER_BASE_URL] == DEFAULT_PARTNER_BASE_URL


@pytest.mark.usefixtures("mock_oauth_patches")
async def test_missing_implementation_missing_configuration(
    hass: HomeAssistant,
) -> None:
    """Abort with missing_configuration when no implementation and no app creds."""

    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={},
        ),
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_application_credentials",
            return_value={},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        # Flow should abort immediately when no implementations exist
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "missing_configuration"


async def test_missing_implementation_missing_credentials(
    hass: HomeAssistant,
) -> None:
    """Abort with missing_credentials when app creds exist but no impl."""

    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={},
        ),
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_application_credentials",
            return_value={DOMAIN: object()},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "missing_credentials"


@pytest.mark.usefixtures("mock_oauth_patches")
async def test_device_code_initiate_failure(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Abort when device code initiation fails."""

    fake_impl = SimpleNamespace(
        domain=DOMAIN,
        name="Level Lock",
        client_id="id",
        redirect_uri="ruri",
        extra_token_resolve_data={},
    )
    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={"impl": fake_impl},
        ),
    ):
        # Override the autouse fixture's mock with a failure response
        aioclient_mock.clear_requests()
        aioclient_mock.post(
            f"{DEFAULT_PARTNER_BASE_URL}{DEVICE_CODE_INITIATE_PATH}",
            status=400,
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "oauth_failed"


@pytest.mark.usefixtures("mock_oauth_patches")
async def test_device_code_initiate_missing_fields(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Abort when device code initiation returns missing fields."""

    fake_impl = SimpleNamespace(
        domain=DOMAIN,
        name="Level Lock",
        client_id="id",
        redirect_uri="ruri",
        extra_token_resolve_data={},
    )
    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={"impl": fake_impl},
        ),
    ):
        # Override the autouse fixture's mock with missing fields response
        aioclient_mock.clear_requests()
        aioclient_mock.post(
            f"{DEFAULT_PARTNER_BASE_URL}{DEVICE_CODE_INITIATE_PATH}",
            json={},  # Missing device_code and user_code
            status=200,
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "oauth_error"


@pytest.mark.usefixtures("mock_oauth_patches")
async def test_device_code_initiate_client_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Abort when device code initiation raises ClientError."""

    fake_impl = SimpleNamespace(
        domain=DOMAIN,
        name="Level Lock",
        client_id="id",
        redirect_uri="ruri",
        extra_token_resolve_data={},
    )
    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={"impl": fake_impl},
        ),
    ):
        # Override the autouse fixture's mock with ClientError
        aioclient_mock.clear_requests()
        aioclient_mock.post(
            f"{DEFAULT_PARTNER_BASE_URL}{DEVICE_CODE_INITIATE_PATH}",
            exc=ClientError(),
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "oauth_failed"


@pytest.mark.usefixtures("mock_oauth_patches")
async def test_device_code_initiate_4xx(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Abort when device code initiation returns 4xx."""

    fake_impl = SimpleNamespace(
        domain=DOMAIN,
        name="Level Lock",
        client_id="id",
        redirect_uri="ruri",
        extra_token_resolve_data={},
    )
    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={"impl": fake_impl},
        ),
    ):
        aioclient_mock.clear_requests()
        aioclient_mock.post(
            f"{DEFAULT_PARTNER_BASE_URL}{DEVICE_CODE_INITIATE_PATH}",
            status=400,
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "oauth_failed"


@pytest.mark.usefixtures("mock_oauth_patches")
async def test_reauth_paths(hass: HomeAssistant) -> None:
    """Test reauth steps show confirm and then return to user."""
    fake_impl = SimpleNamespace(
        domain=DOMAIN,
        name="Level Lock",
        client_id="id",
        redirect_uri="ruri",
        extra_token_resolve_data={},
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "auth_implementation": DOMAIN,
            "token": {
                "access_token": "at",
                "refresh_token": "rt",
                "expires_at": 9999999999,
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        },
        unique_id="uid-re",
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.levelhome.config_flow.config_entry_oauth2_flow.async_get_implementations",
            return_value={"impl": fake_impl},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reauth_confirm"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"


def test_extra_authorize_data_property() -> None:
    """Directly verify extra_authorize_data returns expected scope."""
    handler = object.__new__(OAuth2FlowHandler)
    assert handler.extra_authorize_data == {"scope": "all"}
