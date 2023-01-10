from meeseeks.context import ChangedRoomMessageCtx, LoginCtx
from meeseeks.serializers import ContextFactory, ContextSerializer
from tests.base import BaseTestClass


class TestContextFactory(BaseTestClass):
    """Tests of ContextFactory class. """

    def test_resister(self):
        ctx_factory = ContextFactory()
        ctx_factory.register('changed', 'stream-room-messages', ChangedRoomMessageCtx)

        self.assertEqual(ctx_factory._creators,
                         {('changed', 'stream-room-messages'): ChangedRoomMessageCtx})

    def test_get_serializer(self):
        """Test of success get_serializer method. """

        serializable = {
            'msg': 'result',
            'id': 'login',
            'result': {
                'id': 'ucPgkuQptW4TTqYH2',
                'token': '5XGsD6i9N4c1qyzIH7a4zigOzj9tBzEnxa2Cu7PkQs3',
                'tokenExpires': {'$date': 1659901043466},
                'type': 'password'
            }
        }
        ctx_factory = ContextFactory()
        login_ctx = LoginCtx
        login_ctx._raw_context = serializable
        ctx_factory.register('result', 'login', LoginCtx)
        result = ctx_factory.get_serializer(serializable, 'result', 'login')

        self.assertIsInstance(result, LoginCtx)
        self.assertEqual(result._raw_context, (serializable, ))

    def test_fail_get_serializer(self):
        """Test of success get_serializer method. """

        serializable = {}
        ctx_factory = ContextFactory()

        with self.assertRaises(ValueError):
            ctx_factory.get_serializer(serializable, 'test', 'test')
