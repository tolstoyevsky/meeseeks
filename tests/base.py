"""Module contains base class for creating tests. """

import asyncio
from unittest import mock, TestCase

from tests.mock_rocket_chat import run_mock_server


class BaseTestClass(TestCase):
    """Base class for creating tests. """

    _mock_api = None
    _mock_proc = None

    @staticmethod
    def async_case(func):
        """Using for run async code in sync method. """

        async def wrapper():
            await func()

        asyncio.run(wrapper())

    @classmethod
    def setUpClass(cls):
        """Launches Rocket.Chat mock server before starting tests. """

        cls._mock_api, cls._mock_proc = run_mock_server()

    @classmethod
    def tearDownClass(cls):
        """Stops Rocket.Chat mock server when tests are completed. """

        cls._mock_proc.terminate()
        cls._mock_proc.wait()

    def setUp(self):
        """Patching variables before run tests. """

        patcher_api_v1 = mock.patch('meeseeks.settings.ROCKET_CHAT_API', self._mock_api)
        self.addCleanup(patcher_api_v1.stop)
        patcher_api_v1.start()
