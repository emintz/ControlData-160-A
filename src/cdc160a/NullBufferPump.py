"""
A vacuous (i.e. no-op) buffer pump emulation

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

from cdc160a.BufferPump import BufferPump, PumpStatus
from cdc160a.Device import Device
from cdc160a.NullDevice import NullDevice
from typing import Final

class NullBufferPump(BufferPump):
    """
    A buffer pump that does nothing and never finishes. This
    is used to emulate hung I/O, which happens when a program
    attempts an invalid I/O operation.
    """
    __null_device: Final[Device] = NullDevice()

    def device(self) -> Device:
        return self.__null_device

    def pump(self, elapsed_cycles: int) -> PumpStatus:
        return PumpStatus.NO_DATA_MOVED
