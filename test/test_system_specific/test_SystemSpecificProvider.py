from unittest import TestCase

import inspect
from system_specific import Factory

class TestSystemSpecificProvider(TestCase):

    def test_console_input_checker(self):
        input_checker = Factory.check_console_for_input()
        assert input_checker is not None
        assert callable(input_checker)
        return_type = inspect.signature(input_checker).return_annotation
        assert return_type == bool
        assert len(inspect.signature(input_checker).parameters.values()) == 0
