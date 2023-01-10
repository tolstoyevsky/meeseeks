"""Module runs imported test cases. """

import unittest

from tests.test_commands_base import TestCommunication, TestCommandsBase, TestDialogsBase
from tests.test_commands_mixins import TestCommandsMixin
from tests.test_context import TestContext, TestContextRoom, TestContextUser
from tests.test_core import TestMeeseeksCore
from tests.test_meeseeks_app import TestMeeseeksBaseApp
from tests.test_restapi import TestRestAPI
from tests.test_serializers import TestContextFactory

if __name__ == '__main__':
    unittest.main()
