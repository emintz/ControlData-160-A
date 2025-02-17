"""
A command line-driven CDC 160-A console.

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

from cdc160a.BaseConsole import BaseConsole
from cdc160a.InputOutput import InputOutput
from cdc160a.IOStatus import IOStatus
from cdc160a.Storage import Storage
from development.CommandReader import CommandReader
from system_specific import Factory
from typing import Callable

from development import CommandInterpreters
from development.Interpreter import Interpreter

class Console(BaseConsole):
    """
    A stopgap console, a stopgap that reads its commands from
    the terminal.
    """

    def __init__(
            self,
            input_checker: Callable[[], bool],
            interpreter: Interpreter):
        self.__buffering = False
        self.__input_checker = input_checker
        self.__interpreter = interpreter
        self.__normal_io_status = IOStatus.IDLE

    def before_instruction_fetch(
            self, storage: Storage,
            input_output: InputOutput) -> None:
        """
        Performs console-related tasks required to fetch an instruction.

        The run loop invokes this method just before it fetches an instruction.
        Implementations should set the jump and stop switch masks in the
        provided Storage and generate an interrupt 10 if one or more jump
        switches is down and one or more stop switches is down.

        :param storage: memory and register file
        :param input_output I/O system
        :return: None
        """
        if not storage.run_stop_status or self.__input_checker():
            self.__interpreter.run(storage, input_output)
        storage.set_jump_switch_mask(self.__interpreter.jump_set_mask())
        storage.set_stop_switch_mask(self.__interpreter.stop_set_mask())
        if (self.__interpreter.jump_down_mask() != 0 and
            self.__interpreter.stop_down_mask() != 0):
            storage.request_interrupt(0o10)
            self.__interpreter.release_down_switches()

    def before_instruction_logic(
            self,
            storage: Storage,
            input_output: InputOutput) -> None:
        """
        Perform console-related tasks required to run instruction logic.

        The run loop invokes this method after it unpacks the instruction
        and determines its effective address. Implementations should halt
        the machine if the user has moved the run/stop switch to stop.

        :param storage: memory and register file
        :param input_output I/O system
        :return: None
        """
        pass

    def before_advance(self, storage: Storage, input_output: InputOutput) -> bool:
        """
        Perform module-related tasks required to advance to the next
        instruction. Implementations should stop and display the console
        if the machine has been halted by HLT, ERR, or for any other reasons.

        To support testing, the run loop will halt when this method
        returns False. Production implementations must always return True.

        :param storage: memory and register file
        :param input_output I/O system
        :return: True if the run loop should keep going, False if the run
                 loop should exit. This is to support PyUnit testing.
                 Production versions must return True.
        """
        self.__buffering = storage.buffering
        self.__normal_io_status = storage.normal_io_status
        return True

    def buffering(self) -> bool:
        return self.__buffering

    def normal_io_status(self) -> IOStatus:
        return self.__normal_io_status


def create_interpreter() -> Interpreter:
    """
    Factory function that creates n interpreter that reads commands from
    the terminal.

    :return: the newly minted Interpreter
    """
    return Interpreter(CommandInterpreters.COMMANDS, CommandReader())

def create_console() -> Console:
    """
    Factory method that creates a Console that takes its input from the
    terminal.

    :return: the newly minted Console
    """
    return Console(
        Factory.check_console_for_input(),
        create_interpreter())

def main() -> None:
    """
    Runs the console in an endless loop. Used for hand-testing the Console

    :return: None
    """
    console = create_console()
    storage = Storage()
    input_output = InputOutput([])
    while True:
        console.before_instruction_fetch(storage, input_output)
        console.before_instruction_logic(storage, input_output)
        console.before_advance(storage, input_output)

if __name__ == "__main__":
    main()
