"""Contains base classes for serializing context classes. """


class ContextFactory:
    """Contains methods for handling context classes. """

    def __init__(self):
        self._creators = {}

    def register(self, method, collection, creator):
        """Register the given class with context. """

        self._creators[(method, collection,)] = creator

    def get_serializer(self, serializable, method, collection):
        """Return object of context. """

        creator = self._creators.get((method, collection,))
        if not creator:
            raise ValueError(collection)

        return creator(serializable)


ctx_factory = ContextFactory()


class ContextSerializer:
    """Contains methods for serializing context. """

    def __init__(self, serializable, method, collection):
        self._serializer = ctx_factory.get_serializer(serializable, method, collection)

    def serialize(self):
        """Return serialized context. """

        self._serializer.serialize()
        return self._serializer
