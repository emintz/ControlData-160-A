
"""
Command interpreter for the character mode console.
"""
from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage
from test_support.Assembler import assembler_from_file
from development.Interpreter import Interpreter
from development.Interpreter import Runner


def is_octal(string: str) -> bool:
    result = 0 < len(string)
    for c in string:
        result = result and '0' <= c <= '7'
        if not result:
            break
    return result

def _check_setting(settings: [str], error_message: str) -> bool:
    result = len(settings) > 0
    if not result:
        print(error_message)
    return result

class AssembleAndRunIfErrorFree(Runner):
    """
    Assemble source from a specified text file. If the assembly produces no
    errors, run the assembled program.
    """
    def __init__(self):
        super().__init__("Assembles directly to memory")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        if _check_setting(settings, "Please provide a file name."):
            assembler = assembler_from_file(settings[0], storage)
            if assembler is not None:
                assembler.run()
            else:
                print("Error: file {0} not found.".format(settings[0]))
        return True

class Clear(Runner):

    def __init__(self):
        super().__init__("Halts the machine, stops I/O, etc.")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        storage.clear()
        input_output.clear()
        return True

class Exit(Runner):

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

    def __init__(self):
        super().__init__("Lists peripheral devices, including status")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        for device in input_output.devices():
            device_status = (
                "open on {0}".format(device.file_name())) \
                if device.is_open() \
                else "closed"
            print("{0}: {1}.".format(device.name(), device_status))

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
    Run the next instruction.
    """

    def __init__(self):
        super().__init__("Runs a single instruction (single-steps)")

    def apply(self, interpreter: Interpreter, storage: Storage, input_output: InputOutput, settings: [str]) -> bool:
        storage.stop()
        return False

class StopSwitch(Runner):
    """
    Set stop switches. Stop switches can be set up, down, or center (i.e. off)
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

# Available commands
COMMANDS = {
    "assemble": AssembleAndRunIfErrorFree(),
    "clear": Clear(),
    "devices": ListDevices(),
    "exit": Exit(),
    "halt": Step(),
    "help": Help(),
    "jump1": JumpSwitch(0),
    "jump2": JumpSwitch(1),
    "jump3": JumpSwitch(2),
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
}
