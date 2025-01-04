"""
System-specific object factory

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

import sys
from typing import Callable
from system_specific.linux import Linux
from system_specific.windows import Windows


def check_console_for_input() -> Callable[[], bool]:
    """
    :return: a system-specific function that checks for pending
    keyboard input
    """
    match sys.platform:
        case "linux":
            return Linux.check_for_input
        case "win32":
            return Windows.check_for_input_win
        case _:
            exception = NotImplemented()
            exception.add_note(
                "No keyboard input checker implemented for {0}.".format(
                    sys.platform))
            raise exception
