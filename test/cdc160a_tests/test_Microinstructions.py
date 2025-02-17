"""
Validates Microinstructions.py

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

import unittest
from unittest import TestCase
import os

from cdc160a import Microinstructions
from cdc160a.Hardware import Hardware
from cdc160a.InputOutput import BufferStatus, InitiationStatus, InputOutput
from cdc160a.NullDevice import NullDevice
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.Storage import InterruptLock
from cdc160a.Storage import MCS_MODE_IND
from cdc160a.Storage import Storage
from tempfile import NamedTemporaryFile
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape
from typing import Final

from cdc160a_tests.test_Instructions import (
    AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS,
    AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS,
    G_ADDRESS,
    INSTRUCTION_ADDRESS,
    READ_AND_WRITE_ADDRESS)

JUMP_ADDRESS: Final[int] = 0o2000
FIRST_WORD_ADDRESS: Final[int] = 0o200
LAST_WORD_ADDRESS_PLUS_ONE: Final[int] = 0o210

_BI_TAPE_INPUT_DATA = [
    0o0000, 0o0001, 0o0200, 0o0210, 0o1111,
    0o4001, 0o4011, 0o4111, 0o4112, 0o4122]

_BI_TAPE_OUTPUT_DATA = [
    0o10, 0o06, 0o04, 0o02, 0o00, 0o01, 0o03, 0o05, 0o07]

_BUFFERED_ENTRANCE = 0o200
_INPUT_BUFFER_EXIT = _BUFFERED_ENTRANCE + len(_BI_TAPE_INPUT_DATA)
_OUTPUT_BUFFER_EXIT = _BUFFERED_ENTRANCE + len(_BI_TAPE_OUTPUT_DATA)

class Test(TestCase):

    def setUp(self) -> None:
        self.bi_tape = HyperLoopQuantumGravityBiTape(
            _BI_TAPE_INPUT_DATA)
        self.paper_tape_reader = PaperTapeReader()
        self.input_output = InputOutput([
            self.paper_tape_reader, self.bi_tape])
        self.storage = Storage()
        self.storage.memory[0, READ_AND_WRITE_ADDRESS] = 0o10
        self.storage.memory[1, READ_AND_WRITE_ADDRESS] = 0o11
        self.storage.memory[2, READ_AND_WRITE_ADDRESS] = 0o12
        self.storage.memory[3, READ_AND_WRITE_ADDRESS] = 0o13
        self.storage.memory[4, READ_AND_WRITE_ADDRESS] = 0o14
        self.storage.memory[5, READ_AND_WRITE_ADDRESS] = 0o15
        self.storage.memory[6, READ_AND_WRITE_ADDRESS] = 0o16
        self.storage.memory[7, READ_AND_WRITE_ADDRESS] = 0o17
        self.storage.memory[0, 0o7777] = 0o77
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.s_register = INSTRUCTION_ADDRESS
        self.storage.relative_storage_bank = 3
        self.storage.run()
        self.hardware = Hardware(self.input_output, self.storage)

    def tearDown(self) -> None:
        self.storage = None

    @staticmethod
    def _create_temp_file(contents: str) -> str:
        with NamedTemporaryFile("w+", delete=False) as temp_file:
            file_name = temp_file.name
            print("Temporary file: {0},".format(temp_file.name))
            temp_file.write(contents)
        return file_name

    def test_a_to_buffer(self) -> None:
        self.storage.set_buffer_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_buffer(self.storage)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_buffer_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_a_to_buffer_entrance_while_buffering(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0o7777
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        self.storage.start_buffering()
        assert Microinstructions.a_to_buffer_entrance(self.hardware) == 2
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1000
        assert self.storage.buffer_entrance_register == 0
        assert self.storage.buffer_exit_register == 0o7777
        assert self.storage.buffering

    def test_a_to_buffer_entrance_register_not_buffering(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        assert Microinstructions.a_to_buffer_entrance(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o102
        assert self.storage.buffer_entrance_register == 0o200
        assert self.storage.buffer_exit_register == 0
        assert not self.storage.buffering

    def test_a_to_buffer_exit_buffering(self) -> None:
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0o7777
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        self.storage.start_buffering()
        assert Microinstructions.a_to_buffer_exit(self.hardware) == 2
        assert self.storage.buffer_entrance_register == 0
        assert self.storage.buffer_exit_register == 0o7777
        assert self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o1000

    def test_a_to_buffer_exit_not_buffering(self) -> None:
        self.storage.buffer_entrance_register = 0
        self.storage.buffer_exit_register = 0o7777
        self.storage.a_register = 0o200
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0105)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        assert Microinstructions.a_to_buffer_exit(self.hardware) == 1
        assert self.storage.buffer_entrance_register == 0
        assert self.storage.buffer_exit_register == 0o200
        assert not self.storage.buffering
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o102

    def test_a_to_direct_buffer(self) -> None:
        self.storage.set_direct_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_s_direct(self.hardware)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_direct_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_a_to_indirect_buffer(self) -> None:
        self.storage.set_indirect_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_s_indirect(self.hardware)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_indirect_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_a_to_relative_buffer(self) -> None:
        self.storage.set_relative_storage_bank(1)
        self.storage.a_register = 0o0330
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.a_to_s_relative(self.hardware)
        assert self.storage.z_register == 0o0330
        assert self.storage.read_relative_bank(READ_AND_WRITE_ADDRESS) == 0o0330

    def test_add_e_to_a(self) -> None:
        self.storage.f_e = 0o31
        self.storage.a_register = 0o1203
        Microinstructions.add_e_to_a(self.hardware)
        assert self.storage.z_register == 0o31
        assert self.storage.a_register == 0o1234
        assert not self.storage.err_status

    def test_add_direct_to_a(self) -> None:
        self.storage.a_register = 0o1203
        self.storage.direct_storage_bank = 4
        self.storage.write_direct_bank(0o40, 0o31)
        self.storage.s_register = 0o40
        Microinstructions.add_direct_to_a(self.hardware)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o31
        assert not self.storage.err_status
        assert self.storage.run_stop_status

    def test_add_indirect_to_a(self) -> None:
        self.storage.a_register = 0o1203
        self.storage.indirect_storage_bank = 4
        self.storage.write_indirect_bank(0o40, 0o31)
        self.storage.s_register = 0o40
        Microinstructions.add_indirect_to_a(self.hardware)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o31
        assert not self.storage.err_status
        assert self.storage.run_stop_status

    def test_add_relative_to_a(self) -> None:
        self.storage.a_register = 0o1203
        self.storage.relative_storage_bank = 4
        self.storage.write_relative_bank(0o40, 0o31)
        self.storage.s_register = 0o40
        Microinstructions.add_relative_to_a(self.hardware)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o31
        assert not self.storage.err_status
        assert self.storage.run_stop_status

    def test_add_specific_to_a(self) -> None:
        self.storage.a_register = 0o1203
        self.storage.write_specific(0o31)
        self.storage.s_register = 0o7777
        Microinstructions.add_specific_to_a(self.hardware)
        assert self.storage.a_register == 0o1234
        assert self.storage.z_register == 0o31
        assert not self.storage.err_status
        assert self.storage.run_stop_status

    def test_and_direct_with_a(self) -> None:
        self.storage.set_direct_storage_bank(5)
        self.storage.a_register = 0o5733
        self.storage.s_register = 0o240
        self.storage.write_absolute(5, self.storage.s_register, 0o6365)
        Microinstructions.and_direct_with_a(self.hardware)
        assert self.storage.z_register == 0o6365
        assert self.storage.a_register == 0o4321

    def test_and_indirect_with_a(self) -> None:
        self.storage.set_indirect_storage_bank(5)
        self.storage.a_register = 0o5733
        self.storage.s_register = 0o240
        self.storage.write_absolute(5, self.storage.s_register, 0o6365)
        Microinstructions.and_indirect_with_a(self.hardware)
        assert self.storage.z_register == 0o6365
        assert self.storage.a_register == 0o4321

    def test_and_relative_with_a(self) -> None:
        self.storage.set_relative_storage_bank(5)
        self.storage.a_register = 0o5733
        self.storage.s_register = 0o240
        self.storage.write_absolute(5, self.storage.s_register, 0o6365)
        Microinstructions.and_relative_with_a(self.hardware)
        assert self.storage.z_register == 0o6365
        assert self.storage.a_register == 0o4321

    def test_bank_control_to_a(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        Microinstructions.bank_controls_to_a(self.hardware)
        assert self.storage.a_register == 0o1234

    def test_block_store_buffer_active(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        self.storage.buffer_entrance_register = 0o200
        self.storage.buffer_exit_register = 0o401
        self.storage.a_register = 0o7654
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0100)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        self.storage.start_buffering()
        assert Microinstructions.block_store(self.hardware) == 2
        self.storage.advance_to_next_instruction()
        assert self.storage.buffer_entrance_register == 0o200
        assert self.storage.buffer_exit_register == 0o401
        assert self.storage.buffering
        assert self.storage.get_program_counter() == 0o1000

    def test_block_store_not_buffering(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        self.storage.buffer_entrance_register = 0o200
        self.storage.buffer_exit_register = 0o401
        self.storage.a_register = 0o7654
        self.storage.p_register = 0o100
        self.storage.write_relative_bank(0o100, 0o0100)
        self.storage.write_relative_bank(0o101, 0o1000)
        self.storage.unpack_instruction()
        assert Microinstructions.block_store(self.hardware) == 0o201
        self.storage.advance_to_next_instruction()
        assert not self.storage.buffering
        assert self.storage.buffer_entrance_register == 0o401
        assert self.storage.buffer_exit_register == 0o401
        assert self.storage.read_buffer_bank(0o177) == 0
        assert self.storage.read_buffer_bank(0o401) == 0
        for address in range(0o200, 0o401):
            assert self.storage.read_buffer_bank(address) == 0o7654
        assert self.storage.get_program_counter() == 0o102

    def test_buffer_entrance_to_a(self) -> None:
        self.storage.buffer_entrance_register = 0o2000
        Microinstructions.buffer_entrance_to_a(self.hardware)
        assert self.storage.a_register == 0o2000

    def test_buffer_entrance_to_direct_and_set_from_a(self) -> None:
        self.storage.set_buffer_storage_bank(0o1)
        self.storage.set_direct_storage_bank(0o2)
        self.storage.set_indirect_storage_bank(0o3)
        self.storage.set_relative_storage_bank(0o4)
        assert self.storage.read_direct_bank(0o63) == 0
        self.storage.a_register = 0o3000
        self.storage.f_e = 0o63
        self.storage.buffer_entrance_register = 0o700
        Microinstructions.buffer_entrance_to_direct_and_set_from_a(
            self.hardware)
        assert self.storage.read_direct_bank(0o63) == 0o700
        assert self.storage.buffer_entrance_register == 0o3000

    def test_buffer_exit_to_a(self) -> None:
        self.storage.buffer_exit_register = 0o2000
        Microinstructions.buffer_exit_to_a(self.hardware)
        assert self.storage.a_register == 0o2000

    def test_clear_buffer_controls(self) -> None:
        self.bi_tape.set_online_status(True)
        temp_file_name = self._create_temp_file("000\n")
        assert self.paper_tape_reader.open(temp_file_name)
        status, valid_request = self.input_output.external_function(
            0o3700)
        assert status == 0o0001
        assert valid_request
        assert self.input_output.device_on_normal_channel() == self.bi_tape
        self.storage.buffer_entrance_register = _BUFFERED_ENTRANCE
        self.storage.buffer_exit_register = _INPUT_BUFFER_EXIT
        assert (self.input_output.initiate_buffer_input(self.storage) ==
                InitiationStatus.STARTED)
        assert (self.input_output.device_on_buffer_channel() ==
                self.bi_tape)
        assert self.input_output.device_on_normal_channel() is None

        status, valid_request = self.input_output.external_function(0o4102)
        assert valid_request
        assert (self.input_output.device_on_buffer_channel() ==
                self.bi_tape)
        assert (self.input_output.device_on_normal_channel() ==
                self.paper_tape_reader)

        self.input_output.clear_buffer_controls()
        assert self.input_output.device_on_buffer_channel() is None
        assert (self.input_output.device_on_normal_channel() ==
                self.paper_tape_reader)

        self.paper_tape_reader.close()
        os.unlink(temp_file_name)
        assert not os.path.exists(temp_file_name)

    def test_clear_interrupt_lock(self) -> None:
        self.storage.interrupt_lock = InterruptLock.LOCKED
        Microinstructions.clear_interrupt_lock(self.hardware)
        assert self.storage.interrupt_lock == InterruptLock.UNLOCK_PENDING

    def test_complement_a(self) -> None:
        self.storage.a_register = 0o7070
        self.storage.complement_a()
        assert self.storage.a_register == 0o0707

    def test_e_complement_to_a(self) -> None:
        # LDN 33
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0433)
        self.storage.unpack_instruction()
        Microinstructions.e_complement_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o33
        assert self.storage.a_register == 0o7744

    def test_e_to_a(self) -> None:
        # LDN 33
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0433)
        self.storage.unpack_instruction()
        Microinstructions.e_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o33
        assert self.storage.a_register == 0o33

    def test_half_write_indirect(self):
        self.storage.s_register = 0o2300
        self.storage.write_indirect_bank(0o2300, 0o1267)
        self.storage.a_register = 0o6534
        Microinstructions.half_write_indirect(self.hardware)
        assert self.storage.read_indirect_bank(0o2300) == 0o1234
        assert self.storage.storage_cycle == MCS_MODE_IND

    def test_initiate_buffer_input_io_running(self) -> None:
        # IBI
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7200)
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.unpack_instruction()
        # Throw the buffer channel into an endless loop by starting
        # buffered I/O with no device selected.
        assert Microinstructions.initiate_buffer_input(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)
        assert self.input_output.device_on_normal_channel() is None
        assert isinstance(
            self.input_output.device_on_buffer_channel(),
            NullDevice)

        # Start buffered input from the BiTape
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.input_output.external_function(0o3700)  # Select BiTape
        self.storage.clear_interrupt_lock()
        assert Microinstructions.initiate_buffer_input(self.hardware) == 2
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200
        assert self.input_output.device_on_normal_channel() is None
        assert isinstance(
            self.input_output.device_on_buffer_channel(),
            NullDevice)

    def test_initiate_buffer_input_no_io_running(self) -> None:
        # IBI
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7200)
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.unpack_instruction()
        self.bi_tape.set_online_status(True)
        self.storage.buffer_entrance_register = _BUFFERED_ENTRANCE
        self.storage.buffer_exit_register = _INPUT_BUFFER_EXIT
        self.input_output.external_function(0o3700)  # Select BiTape
        self.storage.clear_interrupt_lock()
        assert Microinstructions.initiate_buffer_input(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)
        assert self.input_output.device_on_normal_channel() is None
        assert self.input_output.device_on_buffer_channel() == self.bi_tape

        while True:
            match self.input_output.buffer(self.storage, 1):
                case BufferStatus.RUNNING:
                    pass
                case BufferStatus.FINISHED:
                    break
                case BufferStatus.FAILURE:
                    self.fail("Unexpected device failure.")

        buffer_memory_address = _BUFFERED_ENTRANCE
        for value in _BI_TAPE_INPUT_DATA:
            assert self.storage.read_buffer_bank(
                buffer_memory_address) == value
            buffer_memory_address += 1

    def test_initiate_buffer_output_io_running(self) -> None:
        # IBO
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7300)
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.unpack_instruction()
        # Throw the buffer channel into an endless loop by starting
        # buffered I/O with no device selected.
        assert Microinstructions.initiate_buffer_output(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)
        assert self.input_output.device_on_normal_channel() is None
        assert isinstance(
            self.input_output.device_on_buffer_channel(),
            NullDevice)

        # Start buffered output from the BiTape
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.input_output.external_function(0o3700)  # Select BiTape
        self.storage.clear_interrupt_lock()
        assert Microinstructions.initiate_buffer_output(self.hardware) == 2
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200
        assert self.input_output.device_on_normal_channel() is None
        assert isinstance(
            self.input_output.device_on_buffer_channel(),
            NullDevice)

    def test_initiate_buffer_output_no_io_running(self) -> None:
        # IBO
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7300)
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.unpack_instruction()

        self.bi_tape.set_online_status(True)
        write_address = _BUFFERED_ENTRANCE
        for value in _BI_TAPE_OUTPUT_DATA:
            self.storage.write_buffer_bank(write_address, value)
            write_address += 1
        self.storage.buffer_entrance_register = _BUFFERED_ENTRANCE
        self.storage.buffer_exit_register = _OUTPUT_BUFFER_EXIT

        self.input_output.external_function(0o3700)  # Select BiTape
        self.storage.clear_interrupt_lock()
        assert Microinstructions.initiate_buffer_output(self.hardware) == 1
        self.storage.advance_to_next_instruction()
        assert (self.storage.get_program_counter() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)
        assert self.input_output.device_on_normal_channel() is None
        assert self.input_output.device_on_buffer_channel() == self.bi_tape

        while True:
            match self.input_output.buffer(self.storage, 1):
                case BufferStatus.RUNNING:
                    pass
                case BufferStatus.FINISHED:
                    break
                case BufferStatus.FAILURE:
                    self.fail("Unexpected device failure.")

        assert self.bi_tape.output_data() == _BI_TAPE_OUTPUT_DATA

    def test_indirect_complement_to_a(self) -> None:
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_indirect_complement_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777

    def test_input_to_a_no_device_selected(self) -> None:
        self.storage.a_register = 0o1234
        assert Microinstructions.input_to_a(self.hardware) == 0
        assert self.storage.a_register == 0o1234
        assert self.storage.machine_hung

    def test_input_device_offline(self) -> None:
        status, valid_request = self.input_output.external_function(
            0o3700)
        assert valid_request
        assert status == 0o4000
        self.storage.a_register = 0o1234
        assert Microinstructions.input_to_a(self.hardware) == 3
        assert self.storage.a_register == 0o1234
        assert self.storage.machine_hung

    def test_input_device_online(self) -> None:
        self.bi_tape.set_online_status(True)
        status , valid_request = self.input_output.external_function(
            0o3700)
        assert valid_request
        assert status == 0o0001
        self.storage.a_register = 0o1234
        assert Microinstructions.input_to_a(self.hardware) == 3
        assert self.storage.a_register == 0o0000
        assert not self.storage.machine_hung

    def test_input_to_memory(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7210)
        self.storage.write_relative_bank(G_ADDRESS, LAST_WORD_ADDRESS_PLUS_ONE)
        self.storage.unpack_instruction()
        self.storage.s_register = FIRST_WORD_ADDRESS

        self.bi_tape.set_online_status(True)
        device_status, valid_request = (
            self.input_output.external_function(0o3700))
        assert valid_request
        assert device_status == 0o0001

        assert Microinstructions.input_to_memory(self.hardware) == 0o10 * 3

        assert self.storage.read_indirect_bank(
            FIRST_WORD_ADDRESS - 1) == 0
        assert self.storage.read_indirect_bank(
            LAST_WORD_ADDRESS_PLUS_ONE) == 0
        for location in range(
                FIRST_WORD_ADDRESS, LAST_WORD_ADDRESS_PLUS_ONE):
            expected_value_index = location - FIRST_WORD_ADDRESS
            assert (self.storage.read_indirect_bank(location) ==
                    _BI_TAPE_INPUT_DATA[expected_value_index])

        assert not self.storage.machine_hung

    def test_multiply_a_by_10(self) -> None:
        # MUT
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0112)
        self.storage.unpack_instruction()
        self.storage.a_register = 1
        Microinstructions.multiply_a_by_10(self.hardware)
        assert not self.storage.err_status
        assert self.storage.a_register == 10

    def test_multiply_a_by_100(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0113)
        self.storage.unpack_instruction()
        self.storage.a_register = 1
        Microinstructions.multiply_a_by_100(self.hardware)
        assert not self.storage.err_status
        assert self.storage.a_register == 100

    def test_p_to_e_direct(self) -> None:
        self.storage.p_register = 0o4132
        self.storage.f_instruction = 0o01
        self.storage.f_e = 0o53
        Microinstructions.p_to_e_direct(self.hardware)
        assert self.storage.read_direct_bank(0o53) == 0o4132

    def test_s_to_a(self) -> None:
        # LDN 37
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0437)
        self.storage.unpack_instruction()
        Microinstructions.e_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o37
        assert self.storage.a_register == 0o37

    def test_direct_complement_to_a(self) -> None:
        self.storage.write_direct_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_direct_complement_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654 ^ 0o7777

    def test_s_direct_to_a(self) -> None:
        self.storage.write_direct_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_direct_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654

    def test_selective_jump_branch(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7720)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o6)
        assert Microinstructions.selective_jump(self.hardware) == 2
        assert self.storage.get_next_execution_address() == 0o200

    def test_selective_jump_no_branch(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7720)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o5)
        assert Microinstructions.selective_jump(self.hardware) == 1
        assert (self.storage.get_next_execution_address() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_selective_stop_halt(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7706)
        self.storage.unpack_instruction()
        self.storage.set_stop_switch_mask(0o2)
        Microinstructions.selective_stop(self.hardware)
        assert not self.storage.run_stop_status

    def test_selective_stop_no_halt(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7706)
        self.storage.unpack_instruction()
        self.storage.set_stop_switch_mask(0o1)
        Microinstructions.selective_stop(self.hardware)
        assert self.storage.run_stop_status

    def test_selective_stop_and_jump_halt_and_branch(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7741)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o4)
        self.storage.set_stop_switch_mask(0o1)
        assert Microinstructions.selective_stop_and_jump(self.hardware) == 2
        assert not self.storage.run_stop_status
        assert self.storage.get_next_execution_address() == 0o200

    def test_selective_stop_and_jump_halt_and_no_branch(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7741)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o2)
        self.storage.set_stop_switch_mask(0o1)
        assert Microinstructions.selective_stop_and_jump(self.hardware) == 1
        assert not self.storage.run_stop_status
        assert (self.storage.get_next_execution_address() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_selective_stop_and_jump_no_halt_and_branch(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7741)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o4)
        self.storage.set_stop_switch_mask(0o2)
        assert Microinstructions.selective_stop_and_jump(self.hardware) == 2
        assert self.storage.run_stop_status
        assert self.storage.get_next_execution_address() == 0o200

    def test_selective_stop_and_jump_no_halt_no_branch(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7741)
        self.storage.unpack_instruction()
        self.storage.write_relative_bank(G_ADDRESS, 0o200)
        self.storage.set_jump_switch_mask(0o1)
        self.storage.set_stop_switch_mask(0o2)
        assert Microinstructions.selective_stop_and_jump(self.hardware) == 1
        assert self.storage.run_stop_status
        assert (self.storage.get_next_execution_address() ==
                AFTER_DOUBLE_WORD_INSTRUCTION_ADDRESS)

    def test_shift_replace_direct(self) -> None:
        self.storage.s_register = 0o40
        self.storage.write_direct_bank(self.storage.s_register, 0o4001)
        Microinstructions.shift_replace_direct(self.hardware)
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o0003
        assert self.storage.read_direct_bank(self.storage.s_register) == 0o0003


    def test_shift_replace_indirect(self) -> None:
        self.storage.s_register = 0o40
        self.storage.write_indirect_bank(self.storage.s_register, 0o4001)
        Microinstructions.shift_replace_indirect(self.hardware)
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o0003
        assert self.storage.read_indirect_bank(self.storage.s_register) == 0o0003

    def test_shift_replace_relative(self) -> None:
        self.storage.s_register = 0o40
        self.storage.write_relative_bank(self.storage.s_register, 0o4001)
        Microinstructions.shift_replace_relative(self.hardware)
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o0003
        assert self.storage.read_relative_bank(self.storage.s_register) == 0o0003

    def test_replace_specific(self) -> None:
        self.storage.write_specific(0o4001)
        Microinstructions.shift_replace_specific(self.hardware)
        assert self.storage.run_stop_status
        assert not self.storage.err_status
        assert self.storage.a_register == 0o0003
        assert self.storage.read_specific() == 0o0003

    def test_jump_forward_indirect(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7110)
        self.storage.s_register = INSTRUCTION_ADDRESS + 0o10
        self.storage.write_relative_bank(
            INSTRUCTION_ADDRESS + 0o10, 0o200)
        self.storage.write_relative_bank(0o200, 0o2000)
        Microinstructions.jump_forward_indirect(self.hardware)
        assert self.storage.get_next_execution_address() == 0o200

    def test_jump_indirect(self) -> None:
        self.storage.write_direct_bank(0o10, 0o2000)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7010)
        self.storage.unpack_instruction()
        Microinstructions.jump_indirect(self.hardware)
        assert not self.storage.err_status
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o2000

    def test_jump_if_a_negative(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_negative(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_negative(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_negative(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7776
        Microinstructions.jump_if_a_negative(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS

    def test_jump_if_a_nonzero(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_nonzero(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_nonzero(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_nonzero(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.nex = 0o7776
        Microinstructions.jump_if_a_nonzero(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS

    def test_jump_if_a_positive(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_positive(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_positive(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_positive(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7776
        Microinstructions.jump_if_a_positive(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_jump_if_a_zero(self) -> None:
        self.__prepare_for_jump()
        self.storage.a_register = 0
        Microinstructions.jump_if_a_zero(self.hardware)
        assert self.storage.next_address() == JUMP_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o0001
        Microinstructions.jump_if_a_zero(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7777
        Microinstructions.jump_if_a_zero(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS
        self.__prepare_for_jump()
        self.storage.a_register = 0o7776
        Microinstructions.jump_if_a_zero(self.hardware)
        assert self.storage.next_address() == AFTER_SINGLE_WORD_INSTRUCTION_ADDRESS

    def test_s_indirect_to_a(self) -> None:
        self.storage.write_indirect_bank(READ_AND_WRITE_ADDRESS, 0o7654)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_indirect_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o7654
        assert self.storage.a_register == 0o7654

    def test_s_relative_complement_to_a(self) -> None:
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_relative_complement_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o13
        assert self.storage.a_register == 0o7764

    def test_rotate_a_left_one(self) -> None:
        self.storage.a_register = 0o0001
        Microinstructions.rotate_a_left_one(self.hardware)
        assert self.storage.a_register == 0x0002
        self.storage.a_register = 0o4001
        Microinstructions.rotate_a_left_one(self.hardware)
        assert self.storage.a_register == 0x0003

    def test_replace_add(self) -> None:
        self.storage.memory[0o3, 0o200] = 0o0777
        self.storage.s_register = 0o200
        self.storage.a_register = 1
        Microinstructions.replace_add(self.hardware, 3)
        assert self.storage.a_register == 0o1000
        assert self.storage.memory[3, 0o200] == 0o1000

    def test_replace_add_direct(self) -> None:
        self.storage.memory[0o3, 0o200] = 0o0777
        self.storage.s_register = 0o200
        self.storage.a_register = 1
        self.storage.direct_storage_bank = 3
        Microinstructions.replace_add_direct(self.hardware)
        assert self.storage.a_register == 0o1000
        assert self.storage.memory[3, 0o200] == 0o1000

    def test_replace_add_indirect(self) -> None:
        self.storage.memory[0o3, 0o200] = 0o0777
        self.storage.s_register = 0o200
        self.storage.a_register = 1
        self.storage.indirect_storage_bank = 3
        Microinstructions.replace_add_indirect(self.hardware)
        assert self.storage.a_register == 0o1000
        assert self.storage.memory[3, 0o200] == 0o1000

    def test_replace_add_relative(self) -> None:
        self.storage.memory[0o3, 0o200] = 0o0777
        self.storage.s_register = 0o200
        self.storage.a_register = 1
        self.storage.relative_storage_bank = 3
        Microinstructions.replace_add_relative(self.hardware)
        assert self.storage.a_register == 0o1000
        assert self.storage.memory[3, 0o200] == 0o1000

    def test_replace_add_specific(self) -> None:
        self.storage.memory[0o0, 0o7777] = 0o0777
        self.storage.s_register = 0o7777
        self.storage.a_register = 1
        Microinstructions.replace_add_specific(self.hardware)
        assert self.storage.a_register == 0o1000
        assert self.storage.memory[0, 0o7777] == 0o1000

    def test_replace_add_one_direct(self) -> None:
        address = 0o20
        self.storage.direct_storage_bank =0o1
        self.storage.memory[0o1, address] = 0o1233
        self.storage.s_register = address
        Microinstructions.replace_add_one_direct(self.hardware)
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.memory[0o1, address] == 0o1234

    def test_replace_add_one_indirect(self) -> None:
        address = 0o20
        self.storage.indirect_storage_bank =0o1
        self.storage.memory[0o1, address] = 0o1233
        self.storage.s_register = address
        Microinstructions.replace_add_one_indirect(self.hardware)
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.memory[0o1, address] == 0o1234

    def test_replace_add_one_relative(self) -> None:
        address = 0o200
        self.storage.relative_storage_bank =0o1
        self.storage.memory[0o1, address] = 0o1233
        self.storage.s_register = address
        Microinstructions.replace_add_one_relative(self.hardware)
        assert not self.storage.err_status
        assert self.storage.a_register == 0o1234
        assert self.storage.memory[0o1, address] == 0o1234

    def test_replace_add_one_specific(self) -> None:
        self.storage.memory[0o0, 0o7777] = 0o1233
        Microinstructions.replace_add_one_specific(self.hardware)
        assert self.storage.read_specific() == 0o1234
        assert self.storage.memory[0o0, 0o7777] == 0o1234

    def test_return_jump(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7100)
        self.storage.write_relative_bank(G_ADDRESS, 0o1000)
        self.storage.s_register = 0o1000
        Microinstructions.return_jump(self.hardware)
        assert (self.storage.read_relative_bank(0o1000) ==
                INSTRUCTION_ADDRESS + 2)
        self.storage.advance_to_next_instruction()
        assert self.storage.p_register == 0o1001

    def test_rotate_a_left_two(self) -> None:
        self.storage.a_register = 0o6000
        Microinstructions.rotate_a_left_two(self.hardware)
        assert self.storage.a_register == 0o0003
        self.storage.a_register = 0o4001
        Microinstructions.rotate_a_left_two(self.hardware)
        assert self.storage.a_register == 0o0006

    def test_rotate_a_left_three(self) -> None:
        self.storage.a_register = 0o7000
        Microinstructions.rotate_a_left_three(self.hardware)
        assert self.storage.a_register == 0o0007

    def test_rotate_a_left_six(self) -> None:
        self.storage.z_register = 0o2143
        self.storage.z_to_a()
        Microinstructions.rotate_a_left_six(self.hardware)
        assert self.storage.z_register == 0o2143
        assert self.storage.a_register == 0o4321

    def test_selective_complement_direct(self) -> None:
        self.storage.direct_storage_bank = 1
        self.storage.write_direct_bank(0o24, 0o14)
        self.storage.s_register = 0o24
        self.storage.a_register = 0o12
        Microinstructions.selective_complement_direct(self.hardware)
        assert self.storage.read_direct_bank(0o24) == 0o14
        assert self.storage.s_register == 0o24
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06

    def test_selective_complement_indirect(self) -> None:
        self.storage.indirect_storage_bank = 1
        self.storage.write_indirect_bank(0o24, 0o14)
        self.storage.s_register = 0o24
        self.storage.a_register = 0o12
        Microinstructions.selective_complement_indirect(self.hardware)
        assert self.storage.read_indirect_bank(0o24) == 0o14
        assert self.storage.s_register == 0o24
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o06

    def test_selective_complement_no_address(self) -> None:
        self.storage.f_e = 0o14
        self.storage.a_register = 0o12
        Microinstructions.selective_complement_no_address(self.hardware)
        assert self.storage.f_e == 0o14
        assert self.storage.a_register == 0o6

    def test_selective_complement_relative(self) -> None:
        self.storage.write_relative_bank(0o200, 0o14)
        self.storage.a_register = 0o12
        self.storage.s_register = 0o200
        Microinstructions.selective_complement_relative(self.hardware)
        assert self.storage.read_relative_bank(0o200) == 0o14
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o6

    def test_set_buf_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0146)
        self.storage.unpack_instruction()
        Microinstructions.set_buf_bank_from_e(self.hardware)
        assert self.storage.buffer_storage_bank == 0o06

    def test_set_dir_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0046)
        self.storage.unpack_instruction()
        Microinstructions.set_dir_bank_from_e(self.hardware)
        assert self.storage.direct_storage_bank == 0o06

    def test_set_dir_ind_rel_bank_from_e_and_jump(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0046)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Microinstructions.set_dir_ind_rel_bank_from_e_and_jump(self.hardware)
        assert self.storage.direct_storage_bank == 0o06
        assert self.storage.indirect_storage_bank == 0o06
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_set_dir_rel_bank_from_e_and_jump(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0046)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Microinstructions.set_dir_rel_bank_from_e_and_jump(self.hardware)
        assert self.storage.direct_storage_bank == 0o06
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_set_ind_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0026)
        self.storage.unpack_instruction()
        Microinstructions.set_ind_bank_from_e(self.hardware)
        assert self.storage.indirect_storage_bank == 0o06

    def test_ind_dir_bank_from_e(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o056)
        self.storage.unpack_instruction()
        Microinstructions.set_ind_dir_bank_from_e(self.hardware)
        assert self.storage.direct_storage_bank == 0o06
        assert self.storage.indirect_storage_bank == 0o06

    def test_ind_rel_bank_from_e_and_jump(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0026)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Microinstructions.set_ind_rel_bank_from_e_and_jump(self.hardware)
        assert self.storage.indirect_storage_bank == 0o06
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_p_to_a(self) -> None:
        self.storage.p_register = 0o4132
        Microinstructions.p_to_a(self.hardware)
        assert self.storage.a_register == 0o4132

    def test_set_rel_bank_from_e_and_jump(self) -> None:
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o0016)
        self.storage.unpack_instruction()
        self.storage.a_register = 0o200
        Microinstructions.set_rel_bank_from_e_and_jump(
            self.hardware)
        assert self.storage.relative_storage_bank == 0o06
        self.storage.advance_to_next_instruction()
        assert self.storage.get_program_counter() == 0o200

    def test_selective_complement_specific(self) -> None:
        self.storage.write_specific(0o14)
        self.storage.a_register = 0o12
        Microinstructions.selective_complement_specific(self.hardware)
        assert self.storage.read_specific() == 0o14
        assert self.storage.z_register == 0o14
        assert self.storage.a_register == 0o6

    def test_shift_a_right_one(self) -> None:
        self.storage.a_register = 0o4000
        Microinstructions.shift_a_right_one(self.hardware)
        assert self.storage.a_register == 0o6000
        self.storage.a_register = 0o6000
        Microinstructions.shift_a_right_one(self.hardware)
        assert self.storage.a_register == 0o7000
        self.storage.a_register = 0o2000
        Microinstructions.shift_a_right_one(self.hardware)
        assert self.storage.a_register == 0o1000
        self.storage.a_register = 0o2002
        Microinstructions.shift_a_right_one(self.hardware)
        assert self.storage.a_register == 0o1001

    def test_shift_a_right_two(self) -> None:
        self.storage.a_register = 0o4000
        Microinstructions.shift_a_right_two(self.hardware)
        assert self.storage.a_register == 0o7000
        self.storage.a_register = 0o2000
        Microinstructions.shift_a_right_one(self.hardware)
        assert self.storage.a_register == 0o1000
        self.storage.a_register = 0o0014
        Microinstructions.shift_a_right_two(self.hardware)
        assert self.storage.a_register == 0o0003
        self.storage.a_register = 0o4014
        Microinstructions.shift_a_right_two(self.hardware)
        assert self.storage.a_register == 0o7003

    def test_s_relative_to_a(self) -> None:
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        Microinstructions.s_relative_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o13
        assert self.storage.a_register == 0o13

    def test_specific_complement_to_a(self) -> None:
        Microinstructions.specific_complement_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o7700

    def test_specific_to_a(self) -> None:
        Microinstructions.specific_to_a(self.hardware)
        assert self.storage.run_stop_status
        assert self.storage.z_register == 0o77
        assert self.storage.a_register == 0o77

    def test_subtract_direct_from_a(self) -> None:
        self.storage.direct_storage_bank = 2
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.a_register = 0o112
        Microinstructions.subtract_direct_from_a(self.hardware)
        assert self.storage.z_register == 0o12
        assert self.storage.a_register == 0o100

    def test_subtract_indirect_from_a(self) -> None:
        self.storage.indirect_storage_bank = 2
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.a_register = 0o112
        Microinstructions.subtract_indirect_from_a(self.hardware)
        assert self.storage.z_register == 0o12
        assert self.storage.a_register == 0o100

    def test_subtract_relative_from_a(self) -> None:
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        self.storage.a_register = 0o113
        Microinstructions.subtract_relative_from_a(self.hardware)
        assert self.storage.z_register == 0o13
        assert self.storage.a_register == 0o100

    def test_subtract_e_from_a(self) -> None:
        self.storage.a_register = 0o1255
        self.storage.f_e = 0o21
        Microinstructions.subtract_e_from_a(self.hardware)
        assert self.storage.z_register == 0o21
        assert self.storage.a_register == 0o1234

    def test_subtract_specific_from_a(self) -> None:
        self.storage.a_register = 0o2234
        self.storage.write_absolute(0, 0o7777, 0o1000)
        Microinstructions.subtract_specific_from_a(self.hardware)
        assert self.storage.z_register == 0o1000
        assert self.storage.a_register == 0o1234

    # Note: the following three tests validate device selection.
    #       It's enough to test the happy path after they run.
    def test_output_a_normal_no_device_selected(self) -> None:
        self.storage.a_register = 0o1414
        assert not self.storage.machine_hung
        assert not self.storage.out_status
        Microinstructions.output_from_a(self.hardware)
        assert self.storage.machine_hung
        assert self.bi_tape.output_data() == []
        assert self.storage.out_status

    def test_output_a_normal_device_offline_and_selected(self) -> None:
        self.input_output.external_function(0o3700)
        self.storage.a_register = 0o1414
        assert not self.storage.machine_hung
        assert not self.storage.out_status
        Microinstructions.output_from_a(self.hardware)
        assert self.storage.machine_hung
        assert self.bi_tape.output_data() == []
        assert self.storage.out_status

    def test_output_a_normal_device_online_and_selected(self) -> None:
        self.bi_tape.set_online_status(True)
        self.input_output.external_function(0o3700)
        self.storage.a_register = 0o1414
        assert not self.storage.machine_hung
        assert not self.storage.out_status
        Microinstructions.output_from_a(self.hardware)
        assert not self.storage.machine_hung
        assert self.bi_tape.output_data() == [0o1414]
        assert self.storage.out_status

    def test_output_no_address_normal_happy_path(self) -> None:
        self.bi_tape.set_online_status(True)
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7421)
        self.storage.unpack_instruction()
        self.input_output.external_function(0o3700)
        self.storage.a_register = 0o1414
        assert not self.storage.machine_hung
        assert not self.storage.out_status
        Microinstructions.output_no_address(self.hardware)
        assert not self.storage.machine_hung
        assert self.bi_tape.output_data() == [0o0021]
        assert self.storage.out_status

    def test_output_from_memory(self) -> None:
        self.bi_tape.set_online_status(True)
        write_location = READ_AND_WRITE_ADDRESS
        for value in _BI_TAPE_INPUT_DATA:
            self.storage.write_indirect_bank(write_location, value)
            write_location += 1
        self.storage.write_relative_bank(INSTRUCTION_ADDRESS, 0o7304)
        self.storage.write_relative_bank(G_ADDRESS, write_location)
        self.storage.unpack_instruction()
        self.input_output.external_function(0o3700)
        self.storage.s_register = READ_AND_WRITE_ADDRESS
        assert self.input_output.write_delay() == 4
        assert Microinstructions.output_from_memory(self.hardware) == 40

    def __prepare_for_jump(self) -> None:
        self.storage.p_register = INSTRUCTION_ADDRESS
        self.storage.s_register = JUMP_ADDRESS

if __name__ == "__main__":
    unittest.main()
