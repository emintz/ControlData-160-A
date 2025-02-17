"""
Validates BootLoader.py

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

from cdc160a.BaseConsole import BaseConsole
from cdc160a.BootLoader import BootLoader
from cdc160a.InputOutput import InputOutput
from cdc160a.PaperTapePunch import PaperTapePunch
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.RunLoop import RunLoop
from cdc160a.Storage import Storage
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape
from test_support.PyunitConsole import PyConsole

class TestBootLoader(TestCase):

    __BOOT_IMAGE: [int] = (
        0o000, 0o000, 0o000, 0o000, 0o000, 0o000, 0o000, 0o000, 0o122, 0o000, 0o112, 0o034, 0o177, 0o000, 0o000, 0o000,
        0o000, 0o000, 0o000, 0o000, 0o000, 0o000,
    )

    def setUp(self) -> None:
        self.__bi_tape: HyperLoopQuantumGravityBiTape = (
            HyperLoopQuantumGravityBiTape(self.__BOOT_IMAGE))
        self.__bi_tape.set_online_status(True)
        self.__console: BaseConsole = PyConsole()
        self.__paper_tape_punch = PaperTapePunch()
        self.__paper_tape_reader = PaperTapeReader()
        self.__input_output = InputOutput([
            self.__bi_tape,
            self.__paper_tape_punch,
            self.__paper_tape_reader])
        self.__storage = Storage()
        self.__run_loop = RunLoop(
            self.__console, self.__storage, self.__input_output)

    def test_load_and_run(self) -> None:
        boot_loader = BootLoader(self.__bi_tape, self.__storage)
        assert boot_loader.status() == BootLoader.Status.IDLE
        self.__storage.p_register = 0o100
        self.__storage.relative_storage_bank = 0o0
        assert boot_loader.load() == BootLoader.Status.SUCCEEDED
        assert self.__storage.get_program_counter() == 0o102
        self.__storage.p_register = 0o100
        self.__storage.a_register = 0
        self.__storage.run()
        self.__run_loop.run()
        assert self.__storage.a_register == 0o1234
        assert self.__storage.get_program_counter() == 0o102
