
"""
Command interpreter for the character mode console.
"""
from cdc160a.Device import Device
from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage
from development.Assembler import assembler_from_file
from development.Interpreter import Interpreter
from development.Interpreter import Runner
from development.MemoryUse import MemoryUsedInBank
from typing import Optional


def is_octal(string: str) -> bool:
    result = 0 < len(string)
    for c in string:
        result = result and '0' <= c <= '7'
        if not result:
            break
    return result

def is_octal_in_range(string: str, min_value: int, max_value: int) -> bool:
    result = is_octal(string)
    if result:
        value = int(string, 8)
        result = min_value <= value <= max_value
    return result

def _check_setting(settings: [str], error_message: str) -> bool:
    result = len(settings) > 0
    if not result:
        print(error_message)
    return result

class AssembleAndRunIfErrorFree(Runner):
    """
    Creates an assembler from the specified source file and, if all
    went well, assembles the source into memory. Note that this
    command does NOT run the assembled code. Use 'run' to run it.
    """
    def __init__(self):
        super().__init__("Assembles directly to memory")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a file name."):
            assembler = assembler_from_file(settings[0], storage)
            if assembler is not None:
                assembler.run()
                interpreter.set_memory_use(assembler.memory_use())
            else:
                print("Error: file {0} not found.".format(settings[0]))
        return True

class Clear(Runner):
    """
    Master clears the emulator, stopping all I/O and resetting
    selected registers
    """
    def __init__(self):
        super().__init__("Halts the machine, stops I/O, etc.")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        storage.clear()
        input_output.clear()
        return True

class Close(Runner):
    def __init__(self):
        super().__init__("Closes the specified device")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a device name"):
            device_key = settings[0]
            device = input_output.device(device_key)
            if device is None:
                print(f"Device {device_key} does not exist.")
            else:
                device.close()
        return True

class Exit(Runner):
    """
    Leaves the emulator.
    """

    def __init__(self):
        super().__init__("Exits the interpreter")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        really_exit = input("Do you really want to quit the emulator (y/N)? ")
        if really_exit.strip() == "y":
            print("Goodbye.")
            exit(0)
        else:
            print("Excellent!")
        return True

class Help(Runner):
    """
    Lists each command and a short description
    """

    def __init__(self):
        super().__init__("Lists commands with descriptions")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        for command_name, command in interpreter.commands().items():
            print(f"{command_name}: {command.help()}")
        return True

class JumpSwitch(Runner):
    """
    Interprets commands that set jump switches.  Switches can be set up, down,
    or center (i.e. off).
    """

    def __init__(self, switch_number: int):
        super().__init__(f"Sets jump switch {switch_number}")
        self.__switch_number = switch_number

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a switch setting."):
            match settings[0]:
                case "center":
                    interpreter.jump_switch_off(self.__switch_number)
                case "down":
                    interpreter.jump_switch_down(self.__switch_number)
                case "up":
                    interpreter.jump_switch_up(self.__switch_number)
                case _:
                    message = "Switch can be set up, down, or sender, found: {0}.".format(settings[0])
                    print(message)
            mask = interpreter.jump_set_mask()
            storage.set_jump_switch_mask(mask)
        return True

class ListDevices(Runner):
    """
    Lists all available peripheral devices and their current status
    """

    def __init__(self):
        super().__init__("Lists peripheral devices, including status")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        for device in input_output.devices():
            device_status = (
                "open on {0}".format(device.file_name())) \
                if device.is_open() \
                else "closed"
            print("{0} ({1}): {2}.".format(
                device.name(), device.key(), device_status))

        return True

class MemoryUse(Runner):
    """
    Prints memory use statistics
    """

    def __init__(self):
        super().__init__("Prints memory use statistics")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        memory_use = interpreter.memory_use()
        print("Memory used:")
        for bank in range(0o0, 0o10):
            print(f"   Bank {bank}: {str(memory_use.memory_use(bank))}")
        return True

class OpenDevice(Runner):
    """
    Opens the specified device. Usually that means attaching the
    device to a user-specified disk file.
    """

    def __init__(self):
        super().__init__("Opens the specified device by attaching it to "
                         "the specified file")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        match len(settings):
            case 0:
                print("Please provide a device name and a file path.")
            case 1:
                print("Please provide a file path")
            case _:
                assert len(settings) >= 2
                device_name = settings[0]
                device = input_output.device(device_name)
                if device is None:
                    print(f"Device {device_name} not found")
                else:
                    device.open(settings[1])
        return True

class Resume(Runner):
    """
    Resumes execution.
    """

    def __init__(self):
        super().__init__("Resumes execution")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        storage.run()
        return False

class SetA(Runner):
    """
    Sets the accumulator (i.e. A register)
    """

    def __init__(self):
        super().__init__("Sets A register value")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a value."):
            value = self._to_int(0o0, 0o7777, settings[0])
            if 0 <= value:
                storage.a_register = value
        return True

class SetB(Runner):
    """
    Set the buffer control bank number
    """

    def __init__(self):
        super().__init__("Sets the buffer storage bank")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a bank number."):
            value = self._to_int(0, 0o7, settings[0])
            if 0 <= value:
                storage.buffer_storage_bank = value
        return True

class SetD(Runner):
    """
    Set the direct storage bank number
    """

    def __init__(self):
        super().__init__("Sets the direct storage bank")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a bank number."):
            value = self._to_int(0o0, 0o7, settings[0])
            if 0 <= value:
                storage.direct_storage_bank = value
        return True

class SetI(Runner):
    """
    Set the indirect storage bank number
    """

    def __init__(self):
        super().__init__("Sets the indirect storage bank")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a bank number."):
            value = self._to_int(0o0, 0o7, settings[0])
            if 0 <= value:
                storage.indirect_storage_bank = value
        return True

class SetP(Runner):
    """
    Set the program address (i.e. P register)
    """

    def __init__(self):
        super().__init__("Sets the P register, the address of the "
                         "next instruction")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide an address."):
            value = self._to_int(0o0, 0o7777, settings[0])
            if 0 <= value:
                storage.p_register = value
        return True

class SetR(Runner):
    """
    Set the relative bank number
    """

    def __init__(self):
        super().__init__("Sets the relative storage bank")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a bank number."):
            value = self._to_int(0o0, 0o7, settings[0])
            if 0 <= value:
                storage.relative_storage_bank = value
        return True

class Step(Runner):
    """
    Run (i.e. "single steps") the next instruction.
    """

    def __init__(self):
        super().__init__("Runs a single instruction (single steps)")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        storage.stop()
        return False

class StopSwitch(Runner):
    """
    Sets stop switches. Stop switches can be set up, down, or center (i.e. off)
    """

    def __init__(self, switch_number: int):
        super().__init__(f"Sets stop switch {switch_number}")
        self.__switch_number = switch_number

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a switch setting."):
            match settings[0]:
                case "center":
                    interpreter.stop_switch_off(self.__switch_number)
                case "down":
                    interpreter.stop_switch_down(self.__switch_number)
                case "up":
                    interpreter.stop_switch_up(self.__switch_number)
                case _:
                    print("Switch can be set center, down, or up, found {0}.".format(settings[0]))
        mask = interpreter.stop_set_mask()
        storage.set_stop_switch_mask(mask)
        return True

class WriteBootTape(Runner):
    """
    Writes the contents of a specified memory bank to the
    paper tape punch in boot format. Take start and end
    addresses from the most recent assembly's memory
    statistics.

    The command writes data to the attached paper tape
    punch, which means:

    1. The emulator must be equipped with an emulated
       paper tape punch.
    2. The punch must be open, i.e. attached to an output
       file.
    3. The attached file must be empty.

    The command takes one argument: a bank number in [0o0 .. 0o7]

    Operating instructions:

    1. Assemble the desired program. DO NOT RUN IT!
    2. Print memory and verify memory use.
    3. Open 'pt_pun', the paper tape punch.
    4. Write the desired bank to the punch. Note
       that the boot image might not be completely
       written to disk when output completes.
    5. Close the paper tape punch. This should
       flush the remaining boot image to the
       disk file.
    6. Enjoy the fruits of your labor.
    """
    def __init__(self):
        super().__init__("Writes memory to the paper tape in boot format")

    @staticmethod
    def __memory_use(interpreter: Interpreter,
            bank: int) -> Optional[MemoryUsedInBank]:
        memory_use: Optional[MemoryUsedInBank] = None
        maybe_memory_use = interpreter.memory_use().memory_use(bank)
        if maybe_memory_use is not None:
            memory_use = maybe_memory_use
        return memory_use

    @staticmethod
    def __paper_tape(input_output: InputOutput) -> Optional[Device]:
        punch = None
        maybe_punch: Optional[Device] = input_output.device("pt_pun")
        if maybe_punch is not None and maybe_punch.is_open():
            punch = maybe_punch
        return punch

    @staticmethod
    def __write_bank_to_boot(bank: int,
            storage: Storage,
            memory_used_in_bank: MemoryUsedInBank,
            punch: Device) -> None:
        # Write leader, 4 words of 0
        for i in range(0, 8):
            punch.write(0)

        # Write the memory image
        for location in range(
                memory_used_in_bank.first_word_address(),
                memory_used_in_bank.last_word_address_plus_one()):
            value = storage.read_absolute(bank, location)
            most_significant = ((value >> 6) & 0o77) | 0o100
            punch.write(most_significant)
            least_significant = value & 0o77
            punch.write(least_significant)

        # Write trailer, 4 words of 0
        for i in range(0, 8):
            punch.write(0)

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if len(settings) < 1:
            print(
                "Please provide the desired bank number.")
        elif not is_octal_in_range(settings[0], 0o0, 0o7):
            print(f"Expected a bank number between 0 and 7 inclusive but "
                  f"found {settings[0]}.")
        else:
            bank = int(settings[0], 8)
            paper_tape_punch: Optional[Device] = self.__paper_tape(input_output)
            memory_used_in_bank = self.__memory_use(interpreter, bank)
            if paper_tape_punch is not None and memory_used_in_bank is not None:
                self.__write_bank_to_boot(
                    bank,
                    storage,
                    memory_used_in_bank,
                    paper_tape_punch)
        return True

# Available commands
COMMANDS = {
    "assemble": AssembleAndRunIfErrorFree(),
    "clear": Clear(),
    "close": Close(),
    "devices": ListDevices(),
    "exit": Exit(),
    "halt": Step(),
    "help": Help(),
    "jump1": JumpSwitch(0),
    "jump2": JumpSwitch(1),
    "jump3": JumpSwitch(2),
    "memory": MemoryUse(),
    "open": OpenDevice(),
    "quit": Exit(),
    "run": Resume(),
    "seta": SetA(),
    "setb": SetB(),
    "setd": SetD(),
    "seti": SetI(),
    "setp": SetP(),
    "setr": SetR(),
    "step": Step(),
    "stop1": StopSwitch(0),
    "stop2": StopSwitch(1),
    "stop3": StopSwitch(2),
    "write_boot_tape": WriteBootTape(),
}
