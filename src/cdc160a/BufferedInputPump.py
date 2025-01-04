"""
Buffered input implementation.

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
from cdc160a.Storage import Storage

class BufferedInputPump(BufferPump):
    """
    Buffers data from an input device to the emulators buffer storage
    bank.
    """

    def __init__(self, device: Device, storage: Storage):
        self.__device = device
        self.__storage = storage
        self.__cycles_remaining = self.__device.initial_read_delay()

    def device(self) -> Device:
        return self.__device

    def pump(self, elapsed_cycles: int) -> PumpStatus:
        self.__cycles_remaining -= elapsed_cycles
        buffer_status = PumpStatus.NO_DATA_MOVED
        if self.__cycles_remaining <= 0:
            self.__cycles_remaining = self.__device.read_delay()
            read_status, datum = self.__device.read()
            if read_status:
                self.__storage.buffer_data_register = datum
                buffer_status = (
                    PumpStatus.ONE_WORD_MOVED) if (
                    self.__storage.buffer_data_to_memory()) else \
                    PumpStatus.COMPLETED
            else:
                buffer_status = PumpStatus.FAILURE
                # TODO(emintz): should we hang here?
        return buffer_status

    def cycles_remaining(self) -> int:
        return self.__cycles_remaining
