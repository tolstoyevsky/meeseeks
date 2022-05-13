from meeseeks import MeeseeksBaseApp
from tests.base import BaseTestClass


class TestMeeseeksApp(BaseTestClass):
    def test_setup(self):
        @self.async_case
        async def body():
            with self.assertLogs() as captured:
                await MeeseeksBaseApp().setup()
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(captured.records[0].getMessage(), 'MeeseeksBaseApp: Started')
