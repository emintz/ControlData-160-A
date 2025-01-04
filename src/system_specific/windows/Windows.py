"""
Windows® keypress sensor

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

Note: msvcrt is only available when running on Windows® whence the
need to bypass its importation on other operating systems.
"""

import sys
if sys.platform == "win32":
    import msvcrt

    def check_for_input_win() -> bool:
        """
        Non-blocking polling key press detector

        :return: True if a key has been pressed (i.e. keyboard input is
                 pending); False otherwise.
        """
        return msvcrt.kbhit()
else:
    def check_for_input_win() -> bool:
        return False
