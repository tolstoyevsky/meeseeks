"""Contains base classes for serializing context classes. """

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from meeseeks.context import Context


class ContextFactory:
    """Contains methods for handling context classes. """

    def __init__(self) -> None:
        self._creators: dict[tuple, Type['Context']] = {}

    def register(self, method: str, collection: str, creator: Type['Context']) -> None:
        """Register the given class with context. """

        self._creators[(method, collection,)] = creator

    def get_serializer(self, serializable: tuple, method: str, collection: str) -> 'Context':
        """Return object of context. """

        creator: Type['Context'] | None = self._creators.get((method, collection,))
        if not creator:
            raise ValueError(collection)

        return creator(serializable)


ctx_factory: ContextFactory = ContextFactory()


class ContextSerializer:
    """Contains methods for serializing context. """

    def __init__(self, serializable: tuple, method: str, collection: str):
        self._serializer = ctx_factory.get_serializer(serializable, method, collection)

    def serialize(self) -> 'Context':
        """Return serialized context. """

        self._serializer.serialize()
        return self._serializer
