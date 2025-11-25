from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceStateInfo")


@_attrs_define
class DeviceStateInfo:
    """Current state information for a device"""

    bolt_state: None | str | Unset = UNSET
    """ Current bolt state (locked, unlocked, etc.) """
    battery_level: None | str | Unset = UNSET
    """ Battery level """
    reachable: bool | None | Unset = UNSET
    """ Whether device is reachable """
    door_sense: None | str | Unset = UNSET
    """ Door sensor state """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bolt_state: None | str | Unset
        if isinstance(self.bolt_state, Unset):
            bolt_state = UNSET
        else:
            bolt_state = self.bolt_state

        battery_level: None | str | Unset
        if isinstance(self.battery_level, Unset):
            battery_level = UNSET
        else:
            battery_level = self.battery_level

        reachable: bool | None | Unset
        if isinstance(self.reachable, Unset):
            reachable = UNSET
        else:
            reachable = self.reachable

        door_sense: None | str | Unset
        if isinstance(self.door_sense, Unset):
            door_sense = UNSET
        else:
            door_sense = self.door_sense

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bolt_state is not UNSET:
            field_dict["bolt_state"] = bolt_state
        if battery_level is not UNSET:
            field_dict["battery_level"] = battery_level
        if reachable is not UNSET:
            field_dict["reachable"] = reachable
        if door_sense is not UNSET:
            field_dict["door_sense"] = door_sense

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_bolt_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        bolt_state = _parse_bolt_state(d.pop("bolt_state", UNSET))

        def _parse_battery_level(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        battery_level = _parse_battery_level(d.pop("battery_level", UNSET))

        def _parse_reachable(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        reachable = _parse_reachable(d.pop("reachable", UNSET))

        def _parse_door_sense(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        door_sense = _parse_door_sense(d.pop("door_sense", UNSET))

        device_state_info = cls(
            bolt_state=bolt_state,
            battery_level=battery_level,
            reachable=reachable,
            door_sense=door_sense,
        )

        device_state_info.additional_properties = d
        return device_state_info

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
