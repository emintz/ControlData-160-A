"""
Validates HyperLoopQuantumGravityBiTape.py

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
from cdc160a.Device import IOChannelSupport
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape

class TestHyperLoopQuantumGravityBiTape(TestCase):

    _INPUT_DATA = [0o0000, 0o0001, 0o0200, 0o0210, 0o1111,
                   0o4001, 0o4011, 0o4111, 0o4112, 0o4122]

    def setUp(self):
        self.__bi_tape = HyperLoopQuantumGravityBiTape(
            self._INPUT_DATA.copy())

    def test_configuration(self) -> None:
        assert self.__bi_tape.can_read()
        assert self.__bi_tape.can_write()
        io_channel_support: IOChannelSupport = (
            self.__bi_tape.io_channel_support())
        assert io_channel_support is IOChannelSupport.NORMAL_AND_BUFFERED
        assert self.__bi_tape.key() == "bi_tape"
        assert self.__bi_tape.file_name() == ""
        assert self.__bi_tape.is_open()

    def test_online_status(self) -> None:
        request_validity, status = (
            self.__bi_tape.external_function(0o3700))
        assert request_validity
        assert status == 0o4000
        self.__bi_tape.set_online_status(True)
        request_validity, status = (
            self.__bi_tape.external_function(0o3700))
        assert request_validity
        assert status == 0o0001
        self.__bi_tape.set_online_status(False)
        request_validity, status = (
            self.__bi_tape.external_function(0o3700))
        assert request_validity
        assert status == 0o4000

    def test_read(self) -> None:
        self.__bi_tape.set_online_status(True)

        for expected_input in self._INPUT_DATA:
            request_validity, status = (
                self.__bi_tape.external_function(0o3700))
            assert request_validity
            assert status == 0o0001
            read_validity, read_value = self.__bi_tape.read()
            assert read_validity
            assert read_value == expected_input

        request_validity, status = (
            self.__bi_tape.external_function(0o3700))
        assert request_validity
        assert status == 0o0000

    def test_read_delay(self) -> None:
        assert self.__bi_tape.read_delay() == 3

    def test_write(self) -> None:
        self.__bi_tape.set_online_status(True)
        expected_output = [0o0001, 0o0010, 0o0100, 0o1000,
                           0o4321, 0o1234, 0o4567, 0o7654]
        for value_to_write in expected_output:
            assert self.__bi_tape.write(value_to_write)

        assert self.__bi_tape.output_data() == expected_output

    def test_write_delay(self) -> None:
        assert self.__bi_tape.write_delay() == 4

    def test_rewind(self) -> None:
        self.__bi_tape.set_online_status(True)
        expected_output: [int] = []

        for expected_input in self._INPUT_DATA:
            request_validity, status = (
                self.__bi_tape.external_function(0o3700))
            assert request_validity
            assert status == 0o0001
            read_validity, read_value = self.__bi_tape.read()
            assert read_validity
            assert read_value == expected_input
            write_value = read_value ^ 0o7777
            expected_output.append(write_value)
            assert self.__bi_tape.write(write_value)

        request_validity, status = self.__bi_tape.external_function(0o3701)
        assert request_validity
        assert status == 0o0001
        assert len(self.__bi_tape.output_data()) == 0
        request_validity, status = self.__bi_tape.external_function(0o3700)
        assert request_validity
        assert status == 0o0001

        for expected_input in self._INPUT_DATA:
            request_validity, status = (
                self.__bi_tape.external_function(0o3700))
            assert request_validity
            assert status == 0o0001
            read_validity, read_value = self.__bi_tape.read()
            assert read_validity
            assert read_value == expected_input

        request_validity, status = (
            self.__bi_tape.external_function(0o3700))
        assert request_validity
        assert status == 0o0000

    def test_change_tape(self) -> None:
        self.__bi_tape.set_online_status(True)

        expected_output = [0o0001, 0o0010, 0o0100, 0o1000,
                           0o4321, 0o1234, 0o4567, 0o7654]
        for value_to_write in expected_output:
            assert self.__bi_tape.write(value_to_write)

        assert self.__bi_tape.output_data() == expected_output

        request_valid, status = self.__bi_tape.external_function(0o3702)
        assert request_valid
        assert status == 0o0001
        assert len(self.__bi_tape.output_data()) == 0

        for expected_input in expected_output:
             valid_read, input_value = self.__bi_tape.read()
             assert valid_read
             assert input_value == expected_input

        request_valid, status = self.__bi_tape.external_function(0o3700)
        assert request_valid
        assert status == 0o0000
