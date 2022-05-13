from meeseeks import RestAPI
from meeseeks.commands import CommandsMixin
from tests.base import BaseTestClass


class TestCommandsMixin(BaseTestClass):
    def test_cmd_rooms_info(self):
        @self.async_case
        async def body():
            commands_mixin = CommandsMixin()
            commands_mixin._restapi = RestAPI({})
