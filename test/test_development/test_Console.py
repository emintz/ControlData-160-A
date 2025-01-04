"""
Validates Console.py

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

from cdc160a.IOStatus import IOStatus
from cdc160a.InputOutput import InputOutput
from cdc160a.PaperTapeReader import PaperTapeReader
from cdc160a.Storage import Storage
from development.CommandInterpreters import COMMANDS
from development.Console import Console
from development.Interpreter import Interpreter

def vacuous_input_checker() -> bool:
    return False

class CommandReaderForTesting:
    def __init__(self):
        self.tokens = [""]

    def read_command(self) -> [str]:
        the_tokens = self.tokens
        self.tokens = [""]
        return the_tokens

"""
Test Console.py, the character-mode console that supports development.
"""
class TestConsole(TestCase):
    pass

    def setUp(self) -> None:
        self.__command_reader = CommandReaderForTesting()
        self.__interpreter = Interpreter(COMMANDS, self.__command_reader)
        self.__paper_tape_reader = PaperTapeReader()
        self.__input_output = InputOutput([self.__paper_tape_reader])
        self.__console = Console(vacuous_input_checker, self.__interpreter)
        self.__storage = Storage()
        self.__storage.run()

    def test_all_switches_centered(self) -> None:
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__storage.interrupt_requests == [False, False, False, False]

    def test_one_jump_switch_up_stop_switches_centered(self) -> None:
        self.__interpreter.jump_switch_up(1)
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0o2
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__storage.interrupt_requests == [False, False, False, False]

    def test_jump_switches_centered_one_stop_switch_up(self) -> None:
        self.__interpreter.stop_switch_up(2)
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__storage.get_stop_switch_mask() == 0o4
        assert self.__storage.interrupt_requests == [False, False, False, False]

    def test_one_jump_switch_up_and_one_stop_switch_up(self) -> None:
        self.__interpreter.jump_switch_up(1)
        self.__interpreter.stop_switch_up(2)
        assert self.__interpreter.jump_set_mask() == 0o2
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__interpreter.stop_set_mask() == 0o4
        assert self.__interpreter.stop_down_mask() == 0
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0o2
        assert self.__storage.get_stop_switch_mask() == 0o4
        assert self.__storage.interrupt_requests == [False, False, False, False]
        assert self.__interpreter.jump_set_mask() == 0o2
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__interpreter.stop_set_mask() == 0o4
        assert self.__interpreter.stop_down_mask() == 0

    def test_one_jump_switch_down_stop_switches_centered(self) -> None:
        self.__interpreter.jump_switch_down(1)
        assert self.__interpreter.jump_set_mask() == 0o2
        assert self.__interpreter.jump_down_mask() == 0o2
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0o2
        assert self.__storage.get_stop_switch_mask() == 0
        assert self.__storage.interrupt_requests == [False, False, False, False]
        assert self.__interpreter.jump_set_mask() == 0o2
        assert self.__interpreter.jump_down_mask() == 0o2
        assert self.__interpreter.stop_set_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0

    def test_jump_switches_centered_one_stop_switch_down(self) -> None:
        self.__interpreter.stop_switch_down(2)
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0
        assert self.__storage.get_stop_switch_mask() == 0o4
        assert self.__storage.interrupt_requests == [False, False, False, False]

    def test_one_jump_switch_down_and_one_stop_switch_up(self) -> None:
        self.__interpreter.jump_switch_down(1)
        assert self.__interpreter.jump_set_mask() == 0o2
        assert self.__interpreter.jump_down_mask() == 0o2
        self.__interpreter.stop_switch_up(2)
        assert self.__interpreter.stop_set_mask() == 0o4
        assert self.__interpreter.stop_down_mask() == 0
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0o2
        assert self.__storage.get_stop_switch_mask() == 0o4
        assert self.__storage.interrupt_requests == [False, False, False, False]
        assert self.__interpreter.jump_set_mask() == 0o2
        assert self.__interpreter.jump_down_mask() == 0o2
        assert self.__interpreter.stop_set_mask() == 0o4
        assert self.__interpreter.stop_down_mask() == 0

    def test_one_jump_switch_up_and_one_stop_switch_down(self) -> None:
        self.__interpreter.jump_switch_up(1)
        self.__interpreter.stop_switch_down(2)
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0o2
        assert self.__storage.get_stop_switch_mask() == 0o4
        assert self.__storage.interrupt_requests == [False, False, False, False]

    def test_one_jump_switch_down_and_one_stop_switch_down(self) -> None:
        self.__interpreter.jump_switch_down(1)
        self.__interpreter.stop_switch_down(2)
        assert self.__interpreter.jump_down_mask() == 0o2
        assert self.__interpreter.stop_down_mask() == 0o4
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        assert self.__storage.run_stop_status
        assert self.__storage.get_jump_switch_mask() == 0o2
        assert self.__storage.get_stop_switch_mask() == 0o4
        assert self.__storage.interrupt_requests == [True, False, False, False]
        assert self.__interpreter.jump_down_mask() == 0
        assert self.__interpreter.stop_down_mask() == 0

    def test_before_advance_no_io(self) -> None:
        self.__console.before_advance(self.__storage, self.__input_output)
        assert not self.__console.buffering()
        assert self.__console.normal_io_status() == IOStatus.IDLE

    def test_before_advance_buffering(self) -> None:
        self.__storage.buffering = True
        self.__console.before_advance(self.__storage, self.__input_output)
        assert self.__console.buffering()
        assert self.__console.normal_io_status() == IOStatus.IDLE

    def test_before_advance_normal_output(self) -> None:
        self.__storage.normal_io_status = IOStatus.OUTPUT
        self.__console.before_advance(self.__storage, self.__input_output)
        assert not self.__console.buffering()
        assert self.__console.normal_io_status() == IOStatus.OUTPUT

if __name__ == '__main__':
    unittest.main()
