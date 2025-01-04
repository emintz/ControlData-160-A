"""
The emulator's run loop.

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

from BaseConsole import BaseConsole
from Hardware import Hardware
from InputOutput import InputOutput
import InstructionDecoder
from Storage import Storage

class RunLoop:
    """
    Run loop for the CDC 160-A emulator.
    """

    def __init__(self, console: BaseConsole, storage: Storage, input_output: InputOutput):
        """
        Constructor. Note that the computer configuration is injected.

        :param input_output:
        :param console: the CDC 160A console. May be a dummy for
               testing under PyUnit, a character-mode console for
               development, or a full-blown GUI.
        :param storage: CDC 160-A memory and register file
        """
        self.__console = console
        self.__input_output = input_output
        self.__storage = storage
        self.__hardware = Hardware(self.__input_output, self.__storage)

    def single_step(self) -> bool:
        """
        Run a single instruction.

        :return: True if emulation should continue, False if the user
                 exits the emulator.
        """
        self.__console.before_instruction_fetch(self.__storage, self.__input_output)
        self.__storage.service_pending_interrupts()
        self.__storage.unpack_instruction()
        decoder = InstructionDecoder.decoder_at(self.__storage.f_instruction)
        current_instruction = decoder.decode(self.__storage.f_e)
        current_instruction.determine_effective_address(self.__storage)
        self.__console.before_instruction_logic(self.__storage, self.__input_output)
        elapsed_cycles = current_instruction.perform_logic(self.__hardware)
        # TODO(emintz): Scaling delay, 6.4 microseconds/cycle
        current_instruction.post_process(self.__hardware)
        self.__input_output.buffer(self.__storage, elapsed_cycles)
        if not self.__console.before_advance(self.__storage, self.__input_output):
            return False
        self.__storage.advance_to_next_instruction()
        return True

    def run(self) -> None:
        """
        Runs the emulator, returning when user exits the emulator.

        :return: None
        """
        while self.single_step():
            pass
