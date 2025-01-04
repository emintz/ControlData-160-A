"""
Validates InputOutput.py

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
import os
from tempfile import NamedTemporaryFile

from cdc160a.Device import Device
from cdc160a.InputOutput import BufferStatus, InitiationStatus, InputOutput
from cdc160a.NullDevice import NullDevice
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.Storage import Storage
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape

_BI_TAPE_INPUT_DATA = [
    0o7777, 0o0001, 0o0200, 0o0210, 0o1111,
    0o4001, 0o4011, 0o4111, 0o4112, 0o4122]
_BUFFER_FIRST_WORD_ADDRESS = 0o200
_INPUT_BUFFER_LAST_WORD_ADDRESS_PLUS_ONE = (
        _BUFFER_FIRST_WORD_ADDRESS + len(_BI_TAPE_INPUT_DATA))
_BI_TAPE_OUTPUT_DATA = [
    0o10, 0o06, 0o04, 0o02, 0o00, 0o01, 0o03, 0o05, 0o07]
_OUTPUT_BUFFER_LAST_WORD_ADDRESS_PLUS_ONE = (
        _BUFFER_FIRST_WORD_ADDRESS + len(_BI_TAPE_OUTPUT_DATA))

class TestInputOutput(TestCase):
    def setUp(self) -> None:
        self.__bi_tape = HyperLoopQuantumGravityBiTape(_BI_TAPE_INPUT_DATA)
        self.__paper_tape_reader = PaperTapeReader()
        self.__input_output = InputOutput(
            [self.__paper_tape_reader, self.__bi_tape])
        self.__storage = Storage()

    def test_buffer_input_when_busy(self) -> None:
        self.__bi_tape.set_online_status(True)
        assert self.__input_output.device_on_normal_channel() is None
        assert self.__input_output.device_on_buffer_channel() is None

        # Throw the buffer into an endless loop.
        self.__init_buffer_registers()
        assert (self.__input_output.initiate_buffer_input(self.__storage) ==
                InitiationStatus.STARTED)
        buffering_device = self.__input_output.device_on_buffer_channel()
        assert self.__input_output.device_on_normal_channel() is None
        assert isinstance(buffering_device, NullDevice)


    def test_buffer_input_no_device_and_buffer_idle(self) -> None:
        self.__bi_tape.set_online_status(True)
        assert self.__input_output.device_on_normal_channel() is None
        assert self.__input_output.device_on_buffer_channel() is None
        self.__init_buffer_registers()
        assert (self.__input_output.initiate_buffer_input(self.__storage) ==
                InitiationStatus.STARTED)
        buffering_device = self.__input_output.device_on_buffer_channel()
        assert self.__input_output.device_on_normal_channel() is None
        assert isinstance(buffering_device, NullDevice)

        device_status, op_status = (
            self.__input_output.external_function(0o3700))
        assert op_status
        assert device_status == 0o0001
        assert isinstance(
            self.__input_output.device_on_normal_channel(),
            HyperLoopQuantumGravityBiTape)

        # Try to select the BiTape. Selection should fail.
        assert (self.__input_output.initiate_buffer_input(self.__storage) ==
                InitiationStatus.ALREADY_RUNNING)
        buffering_device = self.__input_output.device_on_buffer_channel()
        assert isinstance(buffering_device, NullDevice)
        assert self.__input_output.device_on_normal_channel() is None


    def test_buffer_input_happy_path(self) -> None:
        self.__bi_tape.set_online_status(True)
        self.__init_buffer_registers()

        device_status, op_status = (
            self.__input_output.external_function(0o3700))
        assert op_status
        assert device_status == 0o0001
        assert isinstance(
            self.__input_output.device_on_normal_channel(),
            HyperLoopQuantumGravityBiTape)

        assert (self.__input_output.initiate_buffer_input(self.__storage) ==
                InitiationStatus.STARTED)
        buffering_device = self.__input_output.device_on_buffer_channel()
        assert self.__input_output.device_on_normal_channel() is None
        assert isinstance(buffering_device, HyperLoopQuantumGravityBiTape)
        assert (self.__storage.interrupt_requests ==
                [False, False, False, False])

        elapsed_cycles = 0
        while True:
            elapsed_cycles += 1
            match self.__input_output.buffer(self.__storage, 1):
                case BufferStatus.RUNNING:
                    pass
                case BufferStatus.FINISHED:
                    break
                case BufferStatus.FAILURE:
                    self.fail("Unexpected device failure.")
        assert elapsed_cycles == 33
        assert self.__storage.interrupt_requests == [False, True, False, False]

        data_location = _BUFFER_FIRST_WORD_ADDRESS
        for expected_value in _BI_TAPE_INPUT_DATA:
            assert (self.__storage.read_buffer_bank(data_location) ==
                    expected_value)
            data_location += 1

    def test_buffered_output_happy_path(self) -> None:
        self.__bi_tape.set_online_status(True)
        self.__init_buffer_registers()

        device_status, op_status = (
            self.__input_output.external_function(0o3700))
        assert op_status
        assert device_status == 0o0001
        assert isinstance(
            self.__input_output.device_on_normal_channel(),
            HyperLoopQuantumGravityBiTape)
        self.__storage.clear_interrupt_lock()

        write_location = _BUFFER_FIRST_WORD_ADDRESS
        for value in _BI_TAPE_OUTPUT_DATA:
            self.__storage.write_buffer_bank(write_location, value)
            write_location += 1

        self.__storage.buffer_entrance_register = _BUFFER_FIRST_WORD_ADDRESS
        self.__storage.buffer_exit_register = (
            _OUTPUT_BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)

        assert (self.__input_output.initiate_buffer_output(self.__storage) ==
                InitiationStatus.STARTED)
        buffering_device = self.__input_output.device_on_buffer_channel()
        assert self.__input_output.device_on_normal_channel() is None
        assert isinstance(buffering_device, HyperLoopQuantumGravityBiTape)
        assert (self.__storage.interrupt_requests ==
                [False, False, False, False])

        elapsed_cycles = 0
        while True:
            elapsed_cycles += 1
            match self.__input_output.buffer(self.__storage, 1):
                case BufferStatus.RUNNING:
                    pass
                case BufferStatus.FINISHED:
                    break
                case BufferStatus.FAILURE:
                    self.fail("Unexpected device failure.")
        assert elapsed_cycles == 40
        assert self.__bi_tape.output_data() == _BI_TAPE_OUTPUT_DATA

    def test_clear(self) -> None:
        with NamedTemporaryFile("w+", delete=False) as temp_file:
            temp_file_name = temp_file.name
            print("Temporary file: {0},".format(temp_file.name))
            temp_file.write("0\n7\n007\n456\n")
        assert self.__paper_tape_reader.open(temp_file_name)
        self.__bi_tape.set_online_status(True)
        self.__input_output.external_function(0o3700)
        self.__input_output.initiate_buffer_input(self.__storage)
        self.__input_output.external_function(0o4102)
        assert (self.__input_output.device_on_buffer_channel() ==
                self.__bi_tape)
        assert (self.__input_output.device_on_normal_channel() ==
                self.__paper_tape_reader)

        self.__input_output.clear()
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None
        self.__paper_tape_reader.close()

        os.unlink(temp_file_name)
        assert not os.path.exists(temp_file_name)

    def test_device_retrieval(self) -> None:
        assert self.__input_output.device("10K-Foobies") is None
        device = self.__input_output.device("bi_tape")
        assert device is not None
        assert isinstance(device, HyperLoopQuantumGravityBiTape)
        device = self.__input_output.device("pt_rdr")
        assert device is not None
        assert isinstance(device, PaperTapeReader)

    def test_devices(self) -> None:
        devices: [Device] = self.__input_output.devices()
        assert len(devices) == 2

    def test_select_no_device_accepts_code(self):
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None
        response, status = self.__input_output.external_function(0o5000)
        assert response is None
        assert not status
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None

    def test_select_device_offline(self) -> None:
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None
        response, status = self.__input_output.external_function(0o4102)
        assert response is None
        assert not status
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None

    def test_select_valid_device(self) -> None:
        temp_file = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(temp_file.name))
        temp_file.write("0\n7\n007\n456\n")
        temp_file.close()

        self.__paper_tape_reader.open(temp_file.name)

        response, status = self.__input_output.external_function(0o4102)
        self.__paper_tape_reader.close()
        os.unlink(temp_file.name)

        assert response is None
        assert status
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() == self.__paper_tape_reader

    def test_read_delay_no_device_selected(self) -> None:
        assert self.__input_output.read_delay() == 0

    def test_read_delay_bi_tape_selected(self) -> None:
        self.__bi_tape.set_online_status(True)
        device_status, valid_request =\
            self.__input_output.external_function(0o3700)
        assert device_status == 0o0001
        assert valid_request
        assert self.__input_output.read_delay() == 3

    def test_read_no_device_selected(self) -> None:
        status, value = self.__input_output.read_normal()
        assert not status
        assert value == 0

    def test_read_device_ready(self) -> None:
        temp_file = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(temp_file.name))
        temp_file.write("456\n")
        temp_file.close()

        self.__paper_tape_reader.open(temp_file.name)

        self.__input_output.external_function(0o4102)
        status, value = self.__input_output.read_normal()
        assert status
        assert value == 0o456

        self.__paper_tape_reader.close()
        os.unlink(temp_file.name)

    def test_write_delay_no_device_selected(self) -> None:
        assert self.__input_output.write_delay() == 0

    def test_write_delay_bi_tape_selected(self) -> None:
        device_status, operation_succeeded = (
            self.__input_output.external_function(0o3700))
        assert operation_succeeded
        assert device_status == 0o4000
        assert self.__input_output.write_delay() == 4

    def test_write_no_device_selected(self) -> None:
        assert not self.__input_output.write_normal(0o4040)

    def test_write_device_selected_and_offline(self) -> None:
        device_status, operation_succeeded = (
            self.__input_output.external_function(0o3700))
        assert operation_succeeded
        assert device_status == 0o4000

        assert not self.__input_output.write_normal(0o4040)
        assert self.__bi_tape.output_data() == []

    def test_write_device_selected_and_ready(self) -> None:
        self.__bi_tape.set_online_status(True)
        device_status, operation_succeeded = (
            self.__input_output.external_function(0o3700))
        assert operation_succeeded
        assert device_status == 0o0001

        assert self.__input_output.write_normal(0o4040)
        assert self.__bi_tape.output_data() == [0o4040]

    def __init_buffer_registers(self) -> None:
        self.__storage.buffer_entrance_register = (
            _BUFFER_FIRST_WORD_ADDRESS)
        self.__storage.buffer_exit_register = (
            _INPUT_BUFFER_LAST_WORD_ADDRESS_PLUS_ONE)
