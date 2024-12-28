"""
Runs commands for the character mode console.

Note: unlike the actual 160-A console, this simulation
      can stop when interrupts are locked out or buffering
      is active. Be warned!
"""
from abc import ABC, abstractmethod

from cdc160a.Device import Device
from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage
from development.SwitchBank import SwitchBank

def is_octal(string: str) -> bool:
    result = 0 < len(string)
    for c in string:
        result = result and '0' <= c <= '7'
        if not result:
            break

    return result

class Runner(ABC):
    """
    Base class for all command runners.
    """
    @abstractmethod
    def apply(
            self,
            interpreter,
            storage: Storage,
            input_output: InputOutput,
            setting: str) -> bool:
        """
        Runs the command. Subclasses must override this method

        :param interpreter: the command interpreter that invoked this
               method and provides an API that allows commands to
               manipulate the console.
        :param storage: the interpreter's memory and register file
        :param input_output: I/O subsystem
        :param setting: command's parameter
        :return: True if the console should keep interpreting commands,
                 False if the interpreter should exit and let the emulator
                 get on with it.
        """
        return True

    @staticmethod
    def _to_int(min_value: int, max_value: int, value: str) -> int:
        """
        Converts a string that represents an octal value into an integer
        having the represented value, then validates the result.

        :param min_value: lowest allowable value, typically 0
        :param max_value: largest allowable value.
        :param value: the string that represents the value. Note that
               values are 12 bit integers that are treated as non-negative
               values in [0, 0o7777
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
                    "Value must be between {0} and {1} inclusive, found {2}.",
                    oct(min_value)[2:], oct(max_value)[2:], value)
        else:
            print("Octal value required, found: {0}.".format(value))
        return result


class Interpreter:
    """
    Command interpreter
    """
    def __init__(self, commands: {str, Runner},  command_reader):
        self.__commands = commands
        self.__command_reader = command_reader
        self.__jump_switches = SwitchBank()
        self.__stop_switches = SwitchBank()

    @staticmethod
    def __print_device(description: str, device: Device | None) -> None:
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

    def run_command(
            self,
            storage: Storage,
            input_output: InputOutput,
            name: str,
            arg: str) -> bool:
        """
        Runs a single console command

        :param storage: emulator memory and register file
        :param input_output: I/O subsystem
        :param name: command name (e.g. halt)
        :param arg: command argument, an octal value
        :return: True if the interpreter should keep running, False if it
                 should return and let the emulator get on with it.
        """
        result = True
        if name in self.__commands:
            result = self.__commands[name].apply(
                self, storage, input_output, arg)
        else:
            print("Unknown command:", name)
        return result

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
            result = self.run_command(storage, input_output, tokens[0], "")
        else:
            result = self.run_command(storage, input_output, tokens[0], tokens[1])
        return result

    def read_and_run_command(
            self, storage: Storage, input_output: InputOutput) -> bool:
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
