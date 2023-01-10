from meeseeks import RestAPI
from meeseeks.commands import CommandsMixin
from tests.base import BaseTestClass


class TestCommandsMixin(BaseTestClass):
    """Tests of CommandsMixin class. """

    def test_cmd_rooms_info(self):
        """Test of success cmd_rooms_info method. """

        @self.async_case
        async def body():
            # TODO: потребуется исправление
            commands_mixin = CommandsMixin()
            commands_mixin._restapi = RestAPI({})
