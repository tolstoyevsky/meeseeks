"""Module contains description of types for Meeseeks. """
from abc import ABC
from typing import Any, Awaitable, TypedDict


class ContextRoomOptions(TypedDict):
    """Typed room context. """

    roomType: str
    roomParticipant: bool
    roomName: str


class CommandMethod(ABC, Awaitable):
    """Attributes type of asynchronous command method. """

    command_name: str
    command_description: str | None
    permissions: list[str] | None

    async def __call__(self) -> Awaitable[Any]:
        pass


class UserInfo(TypedDict):
    """Typed user information from Rocket.Chat server response. """

    _id: str
    createdAt: str
    services: dict
    emails: list[dict[str, str | bool]]
    type: str
    status: str
    active: bool
    roles: list[str]
    name: str
    lastLogin: str
    utcOffset: int
    username: str
    statusText: str
    requirePasswordChange: bool
    canViewAllInfo: bool
