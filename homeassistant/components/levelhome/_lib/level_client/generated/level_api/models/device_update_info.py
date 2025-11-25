from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_state_info import DeviceStateInfo


T = TypeVar("T", bound="DeviceUpdateInfo")


@_attrs_define
class DeviceUpdateInfo:
    """Information about an added or updated device"""

    device_uuid: str
    """ Canonical ID of device """
    device_name: str
    """ Name of the device """
    serial_number: str
    """ Device serial number """
    product: str
    """ Product type """
    location_uuid: str
    """ Canonical ID of location containing device """
    location_name: str
    """ Name of the location """
    device_state: DeviceStateInfo | Unset = UNSET
    """ Current state information for a device """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        device_uuid = self.device_uuid

        device_name = self.device_name

        serial_number = self.serial_number

        product = self.product

        location_uuid = self.location_uuid

        location_name = self.location_name

        device_state: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device_state, Unset):
            device_state = self.device_state.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_uuid": device_uuid,
                "device_name": device_name,
                "serial_number": serial_number,
                "product": product,
                "location_uuid": location_uuid,
                "location_name": location_name,
            }
        )
        if device_state is not UNSET:
            field_dict["device_state"] = device_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_state_info import DeviceStateInfo

        d = dict(src_dict)
        device_uuid = d.pop("device_uuid")

        device_name = d.pop("device_name")

        serial_number = d.pop("serial_number")

        product = d.pop("product")

        location_uuid = d.pop("location_uuid")

        location_name = d.pop("location_name")

        _device_state = d.pop("device_state", UNSET)
        device_state: DeviceStateInfo | Unset
        if isinstance(_device_state, Unset):
            device_state = UNSET
        else:
            device_state = DeviceStateInfo.from_dict(_device_state)

        device_update_info = cls(
            device_uuid=device_uuid,
            device_name=device_name,
            serial_number=serial_number,
            product=product,
            location_uuid=location_uuid,
            location_name=location_name,
            device_state=device_state,
        )

        device_update_info.additional_properties = d
        return device_update_info

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
