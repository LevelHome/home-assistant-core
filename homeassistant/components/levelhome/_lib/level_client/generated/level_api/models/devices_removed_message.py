from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_type import MessageType, check_message_type

T = TypeVar("T", bound="DevicesRemovedMessage")


@_attrs_define
class DevicesRemovedMessage:
    """Notification sent when devices are removed"""

    type_: MessageType
    """ Type of websocket message """
    device_uuids: list[str]
    """ Array of device canonical IDs that were removed """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        device_uuids = self.device_uuids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "device_uuids": device_uuids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = check_message_type(d.pop("type"))

        device_uuids = cast(list[str], d.pop("device_uuids"))

        devices_removed_message = cls(
            type_=type_,
            device_uuids=device_uuids,
        )

        devices_removed_message.additional_properties = d
        return devices_removed_message

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
