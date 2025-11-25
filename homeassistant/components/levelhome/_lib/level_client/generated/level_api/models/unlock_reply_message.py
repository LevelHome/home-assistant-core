from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_type import MessageType, check_message_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="UnlockReplyMessage")


@_attrs_define
class UnlockReplyMessage:
    """Response to unlock request"""

    type_: MessageType
    """ Type of websocket message """
    device_uuid: str
    success: bool
    """ Whether unlock operation succeeded """
    error: None | str | Unset = UNSET
    """ Error message if operation failed """
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        device_uuid = self.device_uuid

        success = self.success

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "device_uuid": device_uuid,
                "success": success,
            }
        )
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = check_message_type(d.pop("type"))

        device_uuid = d.pop("device_uuid")

        success = d.pop("success")

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        unlock_reply_message = cls(
            type_=type_,
            device_uuid=device_uuid,
            success=success,
            error=error,
        )

        unlock_reply_message.additional_properties = d
        return unlock_reply_message

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
