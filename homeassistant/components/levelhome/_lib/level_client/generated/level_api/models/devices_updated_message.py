from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_type import MessageType, check_message_type

if TYPE_CHECKING:
    from ..models.device_update_info import DeviceUpdateInfo


T = TypeVar("T", bound="DevicesUpdatedMessage")


@_attrs_define
class DevicesUpdatedMessage:
    """Notification sent when devices are added or updated"""

    type_: MessageType
    """ Type of websocket message """
    devices: list[DeviceUpdateInfo]
    """ Array of devices that were added or updated """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        devices = []
        for devices_item_data in self.devices:
            devices_item = devices_item_data.to_dict()
            devices.append(devices_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "devices": devices,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_update_info import DeviceUpdateInfo

        d = dict(src_dict)
        type_ = check_message_type(d.pop("type"))

        devices = []
        _devices = d.pop("devices")
        for devices_item_data in _devices:
            devices_item = DeviceUpdateInfo.from_dict(devices_item_data)

            devices.append(devices_item)

        devices_updated_message = cls(
            type_=type_,
            devices=devices,
        )

        devices_updated_message.additional_properties = d
        return devices_updated_message

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
