"""Module containing Meeseeks commands decorators. """

import asyncio
from functools import wraps

from meeseeks.exceptions import CommandParamNotSpecified, PermissionMissing


class CommandDecorator:
    """A base class that can either be used as a command method decorator to configure it. """

    def configure(self, func_self, *args, **kwargs):
        """Runs before the decorated function. Can interrupt Meeseeks command execution. """

        raise NotImplementedError

    def configure_meta(self, decorated_func):
        """Pass meta data to decorated function. """

    def _decorate_callable(self, func):
        """Wraps decorating function. """

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def inner(func_self, *args, **kwargs):
                await self.configure(func_self, *args, **kwargs)
                return await func(func_self, *args, **kwargs)
        else:
            @wraps(func)
            def inner(func_self, *args, **kwargs):
                self.configure(func_self, *args, **kwargs)
                return func(func_self, *args, **kwargs)

        self.configure_meta(inner)

        return inner

    def __call__(self, decorated, *args, **kwargs):
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

    def __init__(self, name=None, permissions=None, description=''):
        self.name = name
        self.permissions = permissions
        self.description = description

        if not self.name:
            raise CommandParamNotSpecified('Command name is not specified')

        super().__init__()

    async def configure(self, func_self, *args, **kwargs):  # pylint: disable=invalid-overridden-method
        """Runs before the decorated function and checks permissions before
        execute Meeseeks command.
        """

        if not await func_self.check_permissions(roles=self.permissions):
            raise PermissionMissing

    def get_description(self, decorated_func):
        """Return description for command. """

        if self.description == '__doc__':
            return decorated_func.__doc__

        return self.description

    def configure_meta(self, decorated_func):
        """Pass name and description to decorated function. """

        decorated_func.command_name = self.name
        decorated_func.command_description = self.get_description(decorated_func)
        decorated_func.permissions = self.permissions
