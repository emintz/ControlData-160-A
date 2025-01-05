"""
Interpreter for commands issued to the command line-driven console

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

from abc import ABC, abstractmethod

from cdc160a.Device import Device
from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage
from development.CommandReader import CommandReader
from development.MemoryUse import MemoryUse
from development.SwitchBank import SwitchBank
from typing import Optional

def is_octal(string: str) -> bool:
    """
    Verifies that the specified string represents a valid
    octal number, i.e. is non-empty and contains only
    characters in ['0' .. '7']

    :param string: input to validate
    :return: True if the input represents a valid octal number,
             False otherwise.
    """
    result = 0 < len(string)
    for c in string:
        result = result and '0' <= c <= '7'
        if not result:
            break

    return result

class Runner(ABC):
    """
    Base class for all command runners that specifies the
    interpreter API and manages the command's help string.
    """

    def __init__(self, help_string):
        self.__help_string = help_string

    @abstractmethod
    def apply(
            self,
            interpreter, storage:
            Storage, input_output:
            InputOutput, settings: [str]) -> bool:
        """
        Runs the command. Subclasses must override this method

        :param interpreter: the command interpreter that invoked this
               method and provides an API that allows commands to
               manipulate the console.
        :param storage: the interpreter's memory and register file
        :param input_output: I/O subsystem
        :param settings: command's parameters
        :return: True if the console should keep interpreting commands,
                 False if the interpreter should exit and let the emulator
                 get on with it.
        """
        return True

    def help(self) -> str:
        return self.__help_string

    @staticmethod
    def _to_int(min_value: int, max_value: int, value: str) -> int:
        """
        Converts a string that represents an octal value into an integer
        having the represented value, then validates the result.

        :param min_value: lowest allowable value, typically 0
        :param max_value: largest allowable value.
        :param value: the string that represents the value. Note that
               values are 12 bit integers that are treated as non-negative
               values in [0 .. 0o7777]
        :return: the converted value if valid, -1 otherwise. The caller
                 must check the result.
        """
        result = -1
        if is_octal(value):
            maybe_result = int(value, 8)
            if min_value <= maybe_result <= max_value:
                result = maybe_result
            else:
                print(
                    "Value must be between {0} and {1} inclusive, "
                    "found {2}.".format(
                        oct(min_value)[2:],
                        oct(max_value)[2:], value))
        else:
            print("Octal value required, found: {0}.".format(value))
        return result


class Interpreter:
    """
    A simple interpreter that runs character mode console
    commands.

    Note: unlike the actual 160-A console, this simulation
          can stop when interrupts are locked or buffering
          is active. Be warned!
    """

    def __init__(
            self, commands: {str, Runner},  command_reader: CommandReader):
        self.__commands: {str, Runner} = commands
        self.__command_reader: CommandReader = command_reader
        self.__jump_switches: SwitchBank = SwitchBank()
        self.__memory_use: MemoryUse = MemoryUse()
        self.__stop_switches: SwitchBank = SwitchBank()

    @staticmethod
    def __print_device(description: str, device: Optional[Device]) -> None:
        """
        Print the active device name if any.
        :param description: device description (e.g. "Buffered device")
        :param device: the active device, or None if no device is active
        :return: None
        """
        print(
            "{0}: {1}".format(description,
                               "None" if device is None else device.name()))

    @staticmethod
    def __to_octal(value: int, length: int) -> str:
        """
        Converts integers to fixed format octal.

        :param value: value to convert
        :param length: number of digits to return
        :return: the formatted value, 0 filled if necessary
        """
        with_prefix = oct(value)
        unjustified = with_prefix[2:]
        justified = unjustified.rjust(length, '0')
        return justified

    def __display(self, storage: Storage, input_output: InputOutput) -> None:
        """
        Display the emulator state

        :param input_output: I/O subsystem
        :param storage: emulator memory and register file
        :return: None
        """
        print()
        print("Jump Switches: 1 {0}, 2 {1}, 3 {2}".format(
            self.__jump_switches.switch_state_name(0),
            self.__jump_switches.switch_state_name(1),
            self.__jump_switches.switch_state_name(2)))
        print("Stop Switches: 1 {0}, 2 {1}, 3 {2}".format(
            self.__stop_switches.switch_state_name(0),
            self.__stop_switches.switch_state_name(1),
            self.__stop_switches.switch_state_name(2)))
        print("BUF: {0}, DIR: {1}, IND: {2}, REL: {3}".format(
            self.__to_octal(storage.buffer_storage_bank, 1),
            self.__to_octal(storage.direct_storage_bank, 1),
            self.__to_octal(storage.indirect_storage_bank, 1),
            self.__to_octal(storage.relative_storage_bank, 1)))
        print("Buffering: {0}, Normal I/O: {1}".format(
              "ACTIVE" if storage.buffering else "IDLE",
              storage.normal_io_status.name))
        print("A: {0}, P: {1}, Interrupt Lock: {2}".format(
            self.__to_octal(storage.a_register, 4),
            self.__to_octal(storage.p_register, 4),
            storage.interrupt_lock))
        self.__print_device(
            "Buffered I/O device ",
            input_output.device_on_buffer_channel())
        self.__print_device(
            "Normal I/O device",
            input_output.device_on_normal_channel())

    def commands(self) -> {str: Runner}:
        return self.__commands

    def run_command(
            self,
            storage: Storage,
            input_output: InputOutput,
            name: str,
            args: [str]) -> bool:
        """
        Runs a single console command

        :param storage: emulator memory and register file
        :param input_output: I/O subsystem
        :param name: command name (e.g. halt)
        :param args: command arguments.
        :return: True if the interpreter should keep running, False if it
                 should return and let the emulator get on with it.
        """
        result = True
        if name in self.__commands:
            result = self.__commands[name].apply(
                self, storage, input_output, args)
        else:
            print("Unknown command:", name)
        return result

    def memory_use(self) -> MemoryUse:
        return self.__memory_use

    def next_command(
            self,
            storage: Storage,
            input_output: InputOutput,
            tokens: [str]) -> bool:
        """
        Read and run the next available console command

        :param storage: emulator memory and register file
        :param input_output: I/O subsystem
        :param tokens: tokenized command
        :return: True if the interpreter should keep running, False if it
                 should return and let the emulator get on with it.
        """
        result = True
        if len(tokens) == 0:
            print("Blank like ignored.")
        elif len(tokens) == 1:
            result = self.run_command(
                storage, input_output, tokens[0], [])
        else:
            result = self.run_command(
                storage, input_output, tokens[0], tokens[1:])
        return result

    def read_and_run_command(
            self, storage: Storage,
            input_output: InputOutput) -> bool:
        """
        Read a command from the input and run it.

        :param storage: emulator memory and register file
        :param input_output: I/O subsystem
        :return: True if the interpreter should keep running, False if it
                 should return and let the emulator get on with it.
        """
        tokens = self.__command_reader.read_command()
        return self.next_command(storage, input_output, tokens)

    def run(self, storage: Storage, input_output: InputOutput) -> None:
        while True:
            self.__display(storage, input_output)
            if not self.read_and_run_command(storage, input_output):
                break
        pass

    def jump_down_mask(self) -> int:
        """
        Return the jump switch down mask which contains three bits, one for
        each switch. The bits are 1 if and only if their corresponding
        switch is down; otherwise they are 0

        :return: the mask described above
        """
        return self.__jump_switches.down_mask()

    def jump_set_mask(self) -> int:
        """
        Return the jump switch set mask which contains three bits, one for
        each switch. The bits are 1 if and only if their corresponding
        switch is not centered; otherwise they are 0

        :return: the mask described above
        """
        return self.__jump_switches.mask()

    def jump_switch_down(self, switch_number: int) -> None:
        """
        Sets the specified jump switch down

        :param switch_number: switch number, 0 - 2
        :return: None
        """
        self.__jump_switches.set_down(switch_number)

    def jump_switch_off(self, switch_number: int) -> None:
        """
        Sets the specified jump switch off, i.e. center

        :param switch_number: switch number, 0 - 2
        :return: None
        """
        return self.__jump_switches.return_to_center(switch_number)

    def jump_switch_up(self, switch_number: int) -> None:
        """
        Sets the specified jump switch up

        :param switch_number: switch number, 0 - 2
        :return: None
        """
        self.__jump_switches.set_up(switch_number)

    def release_down_switches(self) -> None:
        """
        Release (i.e. return to their centers) all jump and stop switches
        that are set down.

        :return: None
        """
        self.__jump_switches.release_down_switches()
        self.__stop_switches.release_down_switches()

    def set_memory_use(self, memory_use: MemoryUse) -> None:
        self.__memory_use = memory_use

    def stop_down_mask(self) -> int:
        """
        Return the stop switch down mask which contains three bits, one for
        each switch. The bits are 1 if and only if their corresponding
        switch is down; otherwise they are 0

        :return: the mask described above
        """
        return self.__stop_switches.down_mask()

    def stop_set_mask(self) -> int:
        """
        Return the stop switch set mask which contains three bits, one for
        each switch. The bits are 1 if and only if their corresponding
        switch is not centered; otherwise they are 0

        :return: the mask described above
        """
        return self.__stop_switches.mask()

    def stop_switch_down(self, switch_number: int) -> None:
        """
        Sets the specified stop switch down

        :param switch_number: switch number, 0 - 2
        :return:
        """
        self.__stop_switches.set_down(switch_number)

    def stop_switch_off(self, switch_number: int) -> None:
        """
        Sets the specified stop switch off, i.e. center

        :param switch_number: switch number, 0 - 2
        :return: None
        """
        return self.__stop_switches.return_to_center(switch_number)

    def stop_switch_up(self, switch_number: int) -> None:
        """
        Sets the specified stop switch up

        :param switch_number: switch number, 0 - 2
        :return: None
        """
        self.__stop_switches.set_up(switch_number)
