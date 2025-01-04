"""
Validates SystemSpecificProvider.py

Copyright © 2025 The System Source Museum, the authors and maintainers,
and others

This file is part of the System Source Museum Control Data 160-A Emulator.

The System Source Museum Control Data 160-A Emulator is free software: you
can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

The System Source Museum Control Data 160-A Emulator is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with the System Source Museum Control Data 160-A Emulator. If not, see
<https://www.gnu.org/licenses/.
"""

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
