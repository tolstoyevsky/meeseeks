"""Module containing Meeseeks exceptions. """


class LogInFailed(Exception):
    """Raises when Meeseeks cannot log in to Rocket.Chat server. """


class CommandParamNotSpecified(Exception):
    """Raises when Meeseeks command parameter is not specified. """


class AbortCommandExecution(Exception):
    """Base class for all exceptions that are raises to abort a command execution.  """


class PermissionMissing(AbortCommandExecution):
    """Raises when user called Meeseeks command without necessary permissions. """


class SerializerError(Exception):
    """Raises when failed to serialize data. """


class CommandDoesNotExist(Exception):
    """Raises when app command does not exist. """


class BadConfigure(Exception):
    """Raise when Meeseeks not configured correctly on Rocket.Chat. """
