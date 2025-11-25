from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InitiateDeviceCodeRequest")


@_attrs_define
class InitiateDeviceCodeRequest:
    client_id: str
    """ OAuth2 client identifier """
    code_challenge: str
    """ PKCE code challenge """
    code_challenge_method: str
    """ PKCE code challenge method """
    delivery_method: str
    """ Method for delivering user code """
    scope: None | str | Unset = UNSET
    """ OAuth2 scope (optional) """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        code_challenge = self.code_challenge

        code_challenge_method = self.code_challenge_method

        delivery_method = self.delivery_method

        scope: None | str | Unset
        if isinstance(self.scope, Unset):
            scope = UNSET
        else:
            scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_id": client_id,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method,
                "delivery_method": delivery_method,
            }
        )
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("client_id")

        code_challenge = d.pop("code_challenge")

        code_challenge_method = d.pop("code_challenge_method")

        delivery_method = d.pop("delivery_method")

        def _parse_scope(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        scope = _parse_scope(d.pop("scope", UNSET))

        initiate_device_code_request = cls(
            client_id=client_id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            delivery_method=delivery_method,
            scope=scope,
        )

        initiate_device_code_request.additional_properties = d
        return initiate_device_code_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
