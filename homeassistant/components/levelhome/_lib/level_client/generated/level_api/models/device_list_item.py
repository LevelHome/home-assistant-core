from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceListItem")


@_attrs_define
class DeviceListItem:
    """Information about a single device"""

    device_uuid: str
    name: str
    """ Device name """
    serial_number: str
    """ Device serial number """
    product: str
    """ Product type """
    location_uuid: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_uuid = self.device_uuid

        name = self.name

        serial_number = self.serial_number

        product = self.product

        location_uuid = self.location_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_uuid": device_uuid,
                "name": name,
                "serial_number": serial_number,
                "product": product,
                "location_uuid": location_uuid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_uuid = d.pop("device_uuid")

        name = d.pop("name")

        serial_number = d.pop("serial_number")

        product = d.pop("product")

        location_uuid = d.pop("location_uuid")

        device_list_item = cls(
            device_uuid=device_uuid,
            name=name,
            serial_number=serial_number,
            product=product,
            location_uuid=location_uuid,
        )

        device_list_item.additional_properties = d
        return device_list_item

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
