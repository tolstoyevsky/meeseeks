"""Module contains Meeseeks commands decorators. """

import asyncio
from functools import wraps
from typing import Callable, TypeVar, TYPE_CHECKING

from meeseeks.exceptions import CommandParamNotSpecified, PermissionMissing
from meeseeks.type import CommandMethod

if TYPE_CHECKING:
    from meeseeks.commands.base import CommandsBase

_T = TypeVar('_T', bound='CommandsBase')


class CommandDecorator:
    """A base class that can either be used as a command method decorator to configure it. """

    async def configure(
            self, func_self: _T, *args: tuple, **kwargs: dict
    ) -> None:
        """Runs before the decorated function. Can interrupt Meeseeks command execution. """

        raise NotImplementedError

    def configure_meta(self, decorated_func: Callable) -> None:
        """Pass meta data to decorated function. """

    def _decorate_callable(self, func: Callable) -> Callable:
        """Wraps decorating function. """

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def inner(func_self: _T, *args: tuple, **kwargs: dict) -> None:
                await self.configure(func_self, *args, **kwargs)
                await func(func_self, *args, **kwargs)
        else:
            @wraps(func)
            async def inner(func_self: _T, *args: tuple, **kwargs: dict) -> None:
                await self.configure(func_self, *args, **kwargs)
                func(func_self, *args, **kwargs)

        self.configure_meta(inner)

        return inner

    def __call__(self, decorated: Callable, *args: tuple, **kwargs: dict) -> Callable:
        if callable(decorated):
            return self._decorate_callable(decorated)

        raise TypeError(f'Cannot decorate object of type {type(decorated)}')


class cmd(CommandDecorator):  # pylint: disable=invalid-name
    """Decorator to mark some methods of Meeseeks App as command. Allows set permissions and
    add metadata to decorated function.

    `name`: human-readable command name to be used when it is run.

    `permissions`: list of roles that are allowed to execute the command

    `description`: optional parameter to set command description, by default is empty.
                   Сan be set to __doc__ to use decorated function doc-string as description.
    """

    def __init__(
            self,
            name: str = '',
            permissions: list[str] | None = None,
            description: str = '',
    ) -> None:
        self.name = name
        self.permissions = permissions
        self.description = description

        if not self.name:
            raise CommandParamNotSpecified('Command name is not specified')

        super().__init__()

    async def configure(
            self, func_self: _T, *args: tuple, **kwargs: dict,
    ) -> None:  # pylint: disable=invalid-overridden-method
        """Runs before the decorated function and checks permissions before
        execute Meeseeks command.
        """

        if (func_self.check_permissions and
                not await func_self.check_permissions(roles=self.permissions)):
            raise PermissionMissing

    def get_description(self, decorated_func: CommandMethod) -> str | None:
        """Return description for command. """

        if self.description == '__doc__':
            return decorated_func.__doc__

        return self.description

    def configure_meta(self, decorated_func: CommandMethod) -> None:  # type: ignore
        """Pass name and description to decorated function. """

        decorated_func.command_name = self.name
        decorated_func.command_description = self.get_description(decorated_func)
        decorated_func.permissions = self.permissions
