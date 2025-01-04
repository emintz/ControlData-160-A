"""
Validates CommandLoop.py

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
from cdc160a.Storage import Storage
from development import CommandInterpreters
from development import Interpreter
from development.CommandReader import CommandReader

class CommandReaderForTesting(CommandReader):
    def __init__(self):
        self.tokens = [""]

    def read_command(self) -> [str]:
        return self.tokens

class TestInterpreter(TestCase):
    # TODO(emintz): write tests.

    def setUp(self) -> None:
        self.__command_reader = CommandReaderForTesting()
        self.__storage = Storage()
        self.__interpreter = Interpreter.Interpreter(
            CommandInterpreters.COMMANDS, self.__command_reader)



if __name__ == "__main__":
    unittest.main()
