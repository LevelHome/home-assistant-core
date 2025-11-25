from typing import Literal, cast

MessageType = Literal[
    "device_state_changed",
    "devices_removed",
    "devices_updated",
    "get_device_state",
    "get_device_state_reply",
    "list_devices",
    "list_devices_reply",
    "lock",
    "lock_reply",
    "ping",
    "pong",
    "unlock",
    "unlock_reply",
]

MESSAGE_TYPE_VALUES: set[MessageType] = {
    "device_state_changed",
    "devices_removed",
    "devices_updated",
    "get_device_state",
    "get_device_state_reply",
    "list_devices",
    "list_devices_reply",
    "lock",
    "lock_reply",
    "ping",
    "pong",
    "unlock",
    "unlock_reply",
}


def check_message_type(value: str) -> MessageType:
    if value in MESSAGE_TYPE_VALUES:
        return cast(MessageType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MESSAGE_TYPE_VALUES!r}")
