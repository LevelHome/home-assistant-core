from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.poll_device_code_request import PollDeviceCodeRequest
from ...models.poll_device_code_response import PollDeviceCodeResponse
from ...types import Response


def _get_kwargs(
    *,
    body: PollDeviceCodeRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth2/device-code/token",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> PollDeviceCodeResponse | None:
    if response.status_code == 200:
        response_200 = PollDeviceCodeResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = PollDeviceCodeResponse.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = PollDeviceCodeResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PollDeviceCodeResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PollDeviceCodeRequest,
) -> Response[PollDeviceCodeResponse]:
    """Poll for device code token

     Polls for access token after user authorization. Returns token or error status.

    Args:
        body (PollDeviceCodeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PollDeviceCodeResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: PollDeviceCodeRequest,
) -> PollDeviceCodeResponse | None:
    """Poll for device code token

     Polls for access token after user authorization. Returns token or error status.

    Args:
        body (PollDeviceCodeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PollDeviceCodeResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PollDeviceCodeRequest,
) -> Response[PollDeviceCodeResponse]:
    """Poll for device code token

     Polls for access token after user authorization. Returns token or error status.

    Args:
        body (PollDeviceCodeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PollDeviceCodeResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PollDeviceCodeRequest,
) -> PollDeviceCodeResponse | None:
    """Poll for device code token

     Polls for access token after user authorization. Returns token or error status.

    Args:
        body (PollDeviceCodeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PollDeviceCodeResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
