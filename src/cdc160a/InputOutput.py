"""
Input/Output emulation

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

from cdc160a.BufferedInputPump import BufferedInputPump
from cdc160a.BufferedOutputPump import BufferedOutputPump
from cdc160a.BufferPump import BufferPump, PumpStatus
from cdc160a.Device import IOChannelSupport
from cdc160a.NullBufferPump import NullBufferPump
from cdc160a.Device import Device
from cdc160a.Storage import Storage
from enum import Enum, unique
from typing import Callable, Optional

@unique
class BufferStatus(Enum):
    """
    Status of a buffered data transfer.
    """
    INACTIVE = 1   # No active buffering, buffer is not running
    RUNNING = 2    # Buffer is active and running well. Note that
                   # this code does not indicate if data was transferred.
    FINISHED = 3   # Buffer just completed, the I/O system has
                   # requested interrupt 20
    FAILURE = 4    # I/O failed. Caller should respond accordingly
                   # TODO(emintz): what should happen here?

@unique
class InitiationStatus(Enum):
    ALREADY_RUNNING = 1  # Buffer already running, cannot initiate
    STARTED = 2          # Buffer started. Completion is not guaranteed.

def _input_pump(device: Device, storage: Storage) -> BufferPump:
    return BufferedInputPump(device, storage)

def _output_pump(device: Device, storage: Storage) -> BufferPump:
    return BufferedOutputPump(device, storage)

def _stop_device(device: Optional[Device]) -> None:
    if device is not None:
        device.stop()

class InputOutput:
    """
    High level input/output emulation, a software data bus connected
    to emulated I/O devices.
    """
    def __init__(self, devices: [Device]):
        """
        Constructor

        :param devices: a list of I/O devices attached to this
                        160-A
        """
        self.__buffer_pump: Optional[BufferPump] = None
        self.__device_dict = {}
        self.__device_on_normal_channel: Optional[Device] = None
        for device in devices:
            self.__device_dict[device.key()] = device

    def buffer(self, storage, cycles: int) -> BufferStatus:
        """
        If buffering is active, try to move one word. Otherwise, do
        nothing.

        :param storage: emulator storage: memory and register file.
        :param cycles: the number of memory cycles elapsed since the
               prior call
        :return: the buffer status specified in the foregoing
                 BufferStatus enumeration
        """
        status: BufferStatus = BufferStatus.INACTIVE
        if self.__buffer_pump is not None:
            match self.__buffer_pump.pump(cycles):
                case PumpStatus.NO_DATA_MOVED:
                    status = BufferStatus.RUNNING
                case PumpStatus.ONE_WORD_MOVED:
                    status = BufferStatus.RUNNING
                case PumpStatus.COMPLETED:
                    self.__buffer_pump = None
                    status = BufferStatus.FINISHED
                    storage.request_interrupt(0o20)
                case PumpStatus.FAILURE:
                    status = BufferStatus.FAILURE
            return status

    def clear(self) -> None:
        """
        Stop normal and buffered I/O and clear all selected devices. This
        supports master clear.

        :return: None
        """
        _stop_device(self.device_on_normal_channel())
        _stop_device(self.device_on_buffer_channel())
        self.__buffer_pump = None
        self.__device_on_normal_channel = None

    def clear_buffer_controls(self) -> None:
        _stop_device(self.device_on_buffer_channel())
        self.__buffer_pump = None

    def device(self, key: str) -> Optional[Device]:
        return self.__device_dict.get(key)

    def devices(self) -> [Device]:
        return self.__device_dict.values()

    def device_on_buffer_channel(self) -> Device:
        return self.__buffer_pump.device() \
            if self.__buffer_pump is not None \
            else None

    def device_on_normal_channel(self) -> Device:
        return self.__device_on_normal_channel

    def external_function(self, operand: int) -> (int | None, bool):
        """
        Perform an external function, select or query a device.

        :param operand: 12 bit function code
        :return: a tuple whose first member is the device response, an
                 integer if the device response or None if it does not,
                 the second a boolean that is True if the request was
                 legal and False if it was illegal. Illegal requests can
                 be a request that an attached device cannot perform (e.g.
                 selecting a powered down device) or a device that does not
                 exist.
        """
        status = False
        response = None
        self.__device_on_normal_channel = None  # Deselect any active device.

        device = None

        for current_device in self.__device_dict.values():
            if current_device.accepts(operand):
                device = current_device
                break

        if device is not None:
            status, response = device.external_function(operand)
            if status:
                self.__device_on_normal_channel = device

        return response, status

    def _initiate_buffered_io(
            self,
            storage: Storage,
            pump_factory: Callable[[Device, Storage], BufferPump]) -> InitiationStatus:
        """
        Initiate buffered I/O. The provided buffer pump factory function
        determines direction (i.e. input or output)

        :param storage: emulator memory and register file
        :param pump_factory: function that provides the required buffer pump

        :return: InitiationStatus.ALREADY_RUNNING if a device
                 is buffering; InitiationStatus.STARTED
                 otherwise. When the call returns
                 InitiationStatus.STARTED, a buffer is running,
                 but completion is not guaranteed.
        """
        status = InitiationStatus.ALREADY_RUNNING
        device_to_buffer = self.__device_on_normal_channel
        self.__device_on_normal_channel = None
        if self.__buffer_pump is None:
            status = InitiationStatus.STARTED
            if device_to_buffer is None:
                self.__buffer_pump = NullBufferPump()
            else:
                use_real_device = (
                        device_to_buffer.can_read()
                        and device_to_buffer.io_channel_support() ==
                            IOChannelSupport.NORMAL_AND_BUFFERED)
                self.__buffer_pump = pump_factory(
                    device_to_buffer, storage) if use_real_device \
                        else NullBufferPump()

        return status


    def initiate_buffer_input(self, storage: Storage) -> InitiationStatus:
        """
        Start buffered input. The caller must have set the
        buffer entrance and buffer exit registers to valid
        values; in particular, the caller must ensure that
        [BER] is strictly less than [BXR]. Behavior is
        unspecified if this preconditiion is violated.

        Note that the device on the normal channel is always
        deselected, even if buffering is in progress
        TODO(emintz): is this proper behavior?
        TODO(emintz): maybe refactor most of the logic into
                      a utility routine shared with
                      initiate_buffer_output?

        :param storage: emulator memory and register file
        :return: InitiationStatus.ALREADY_RUNNING if a device
                 is buffering; InitiationStatus.STARTED
                 otherwise. When the call returns
                 InitiationStatus.STARTED, a buffer is running,
                 but completion is not guaranteed.
        """
        return self._initiate_buffered_io(storage, _input_pump)

    def initiate_buffer_output(self, storage: Storage) -> InitiationStatus:
        """
        Start buffered output. The caller must have set the
        buffer entrance and buffer exit registers to valid
        values; in particular, the caller must ensure that
        [BER] is strictly less than [BXR]. Behavior is
        unspecified if this preconditiion is violated.

        Note that the device on the normal channel is always
        deselected, even if buffering is in progress
        TODO(emintz): is this proper behavior?
        TODO(emintz): maybe refactor most of the logic into
                      a utility routine shared with
                      initiate_buffer_input?

        :param storage: emulator memory and register file
        :return: InitiationStatus.ALREADY_RUNNING if a device
                 is buffering; InitiationStatus.STARTED
                 otherwise. When the call returns
                 InitiationStatus.STARTED, a buffer is running,
                 but completion is not guaranteed.
        """
        return self._initiate_buffered_io(storage, _output_pump)

    def read_delay(self) -> int:
        """
        :return: the selected normal I/O device's read delay or
                 0 if no device selected for normal I.O
        """
        return self.__device_on_normal_channel.read_delay() \
            if self.__device_on_normal_channel is not None \
            else 0

    def read_normal(self) -> (bool, int):
        """
        If a device has been selected on the normal channel, read one
        word; otherwise fail.

        :return: read status, True if successful and False otherwise,
                 and the value read. The value will be 0 on failure.
        """
        status = False
        data = 0
        if self.__device_on_normal_channel is not None:
            status, data = self.__device_on_normal_channel.read()
        return status, data

    def write_delay(self) -> int:
        """
        :return: the selected normal I/O device's read delay or
                 0 if no device selected for normal I.O
        """
        return self.__device_on_normal_channel.write_delay() \
            if self.__device_on_normal_channel is not None \
            else 0

    def write_normal(self, value: int) -> bool:
        """
        Write one word to the device on the normal I/O channel if
        a devices has been selected for normal I/O
        :param value: word to write
        :return: True if a device was selected for normal I/O and
                 output succeeded, False otherwise.
        """
        return self.__device_on_normal_channel.write(value) \
            if self.__device_on_normal_channel is not None \
            else False
