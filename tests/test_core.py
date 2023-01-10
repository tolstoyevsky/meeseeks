from unittest import mock

from meeseeks import MeeseeksCore, RestAPI, MeeseeksBaseApp
from meeseeks.exceptions import BadConfigure
from tests.base import BaseTestClass


class TestMeeseeksCore(BaseTestClass):
    """Tests of MeeseeksCore class."""

    @mock.patch('meeseeks.settings.USERS_LIST_REQUEST', '/users.list_without_permissons/')
    def test_fail_check_bot_permissions(self):
        """Test of failure check_bot_permissions method. """

        @self.async_case
        async def body():
            core = MeeseeksCore()
            core._restapi = RestAPI({})
            core._user_id = 'X2gR7ZHZdmsrTSDRK'

            with self.assertRaises(BadConfigure):
                await core.check_bot_permissions()

    def test_check_app_name(self):
        """Test of success check_app_name method. """

        @self.async_case
        async def body():
            app = MeeseeksBaseApp()
            app.app_name = ''

            with self.assertRaises(NotImplementedError):
                MeeseeksCore.check_app_name(app)

    @mock.patch('meeseeks.settings.INSTALLED_APPS', ('meeseeks.MeeseeksBaseApp', ))
    def test_init_apps(self):
        """Test of success _init_apps method. """

        core = MeeseeksCore()
        apps_instances = core._init_apps()

        self.assertIsInstance(apps_instances[0], MeeseeksBaseApp)
