from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PollDeviceCodeRequest")


@_attrs_define
class PollDeviceCodeRequest:
    client_id: str
    """ OAuth2 client identifier """
    device_code: str
    """ Device code from initiate response """
    grant_type: str
    """ OAuth2 grant type """
    code_verifier: str
    """ PKCE code verifier """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        device_code = self.device_code

        grant_type = self.grant_type

        code_verifier = self.code_verifier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_id": client_id,
                "device_code": device_code,
                "grant_type": grant_type,
                "code_verifier": code_verifier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("client_id")

        device_code = d.pop("device_code")

        grant_type = d.pop("grant_type")

        code_verifier = d.pop("code_verifier")

        poll_device_code_request = cls(
            client_id=client_id,
            device_code=device_code,
            grant_type=grant_type,
            code_verifier=code_verifier,
        )

        poll_device_code_request.additional_properties = d
        return poll_device_code_request

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
