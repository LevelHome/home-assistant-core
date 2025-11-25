from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_type import MessageType, check_message_type

T = TypeVar("T", bound="UnlockMessage")


@_attrs_define
class UnlockMessage:
    """Request to unlock a device"""

    type_: MessageType
    """ Type of websocket message """
    device_uuid: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        device_uuid = self.device_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "device_uuid": device_uuid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = check_message_type(d.pop("type"))

        device_uuid = d.pop("device_uuid")

        unlock_message = cls(
            type_=type_,
            device_uuid=device_uuid,
        )

        unlock_message.additional_properties = d
        return unlock_message

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
