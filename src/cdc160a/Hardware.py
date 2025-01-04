"""
Container for specialized CDC160-A hardware emulations.

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

from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage

class Hardware:
    """
    Holds all hardware components so we can pass them around easily.
    """
    def __init__(self, input_output: InputOutput, storage: Storage):
        """
        Constructor

        :param input_output: I/O hardware emulation
        :param storage: memory and register file emulation
        """
        self.input_output = input_output
        self.storage = storage
