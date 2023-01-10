from meeseeks import MeeseeksBaseApp
from tests.base import BaseTestClass


class TestMeeseeksBaseApp(BaseTestClass):
    """Tests of MeeseeksBaseApp class. """

    def test_setup(self):
        """Test of success setup method. """

        @self.async_case
        async def body():
            with self.assertLogs() as captured:
                await MeeseeksBaseApp().setup()
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(captured.records[0].getMessage(), 'MeeseeksBaseApp: Started')
