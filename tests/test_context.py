from meeseeks.context import Context, ContextRoom, ContextUser
from tests.base import BaseTestClass


class TestContext(BaseTestClass):
    """Tests of Context class. """

    def test_serialize(self):
        """Test of success serialize method. """

        with self.assertRaises(NotImplementedError):
            Context(()).serialize()


class TestContextUser(BaseTestClass):
    """Tests of ContextUser class. """

    def test_init(self):
        """Test of success __init__ method. """

        result = ContextUser('X2gR7ZHZdmsrTSDRK', 'test', 'Test')

        self.assertEqual(result.id, 'X2gR7ZHZdmsrTSDRK')
        self.assertEqual(result.username, 'test')
        self.assertEqual(result.name, 'Test')


class TestContextRoom(BaseTestClass):
    """Tests of ContextRoom class."""

    def test_init(self):
        """Test of success __init__ method. """

        result = ContextRoom(
            'general',
            {'roomType': 'c', 'roomParticipant': True, 'roomName': 'General'},
        )

        self.assertEqual(result.id, 'general')
        self.assertEqual(result.type, 'c')
        self.assertEqual(result.participant, True)
        self.assertEqual(result.name, 'General')
