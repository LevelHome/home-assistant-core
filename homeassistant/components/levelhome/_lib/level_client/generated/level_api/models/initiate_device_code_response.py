from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InitiateDeviceCodeResponse")


@_attrs_define
class InitiateDeviceCodeResponse:
    device_code: str
    """ Device code to poll for token """
    user_code: str
    """ User code to display to user """
    expires_in: int
    """ Seconds until device code expires """
    interval: int
    """ Minimum seconds between polling requests """
    verification_uri: str | Unset = UNSET
    """ URI where user enters code """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_code = self.device_code

        user_code = self.user_code

        expires_in = self.expires_in

        interval = self.interval

        verification_uri = self.verification_uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_code": device_code,
                "user_code": user_code,
                "expires_in": expires_in,
                "interval": interval,
            }
        )
        if verification_uri is not UNSET:
            field_dict["verification_uri"] = verification_uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_code = d.pop("device_code")

        user_code = d.pop("user_code")

        expires_in = d.pop("expires_in")

        interval = d.pop("interval")

        verification_uri = d.pop("verification_uri", UNSET)

        initiate_device_code_response = cls(
            device_code=device_code,
            user_code=user_code,
            expires_in=expires_in,
            interval=interval,
            verification_uri=verification_uri,
        )

        initiate_device_code_response.additional_properties = d
        return initiate_device_code_response

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
