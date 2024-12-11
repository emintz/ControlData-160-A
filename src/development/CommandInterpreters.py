
"""
Command interpreter for the character mode console.
"""
from cdc160a.Storage import Storage
from test_support.Assembler import Assembler, assembler_from_file
from development.Interpreter import Interpreter
from development.Interpreter import Runner


def is_octal(string: str) -> bool:
    result = 0 < len(string)
    for c in string:
        result = result and '0' <= c <= '7'
        if not result:
            break
    return result

class AssembleAndRunIfErrorFree(Runner):
    """
    Assemble source from a specified text file. If the assembly produces no
    errors, run the assembled program.
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        assembler = assembler_from_file(setting, storage)
        if assembler is not None:
            assembler.run()
        else:
            print("Error: file {0} not found.".format(setting))
        return True

class Exit(Runner):

    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        really_exit = input("Do you really want to quit the interpreter (y/N)? ")
        if really_exit.strip() == "y":
            print("Goodbye.")
            exit(0)
        else:
            print("Excellent!")
        return True

class JumpSwitch(Runner):
    """
    Interprets commands that set jump switches.  Switches can be set up, down,
    or center (i.e. off).
    """

    def __init__(self, switch_number: int):
        self.__switch_number = switch_number

    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        match setting:
            case "center":
                interpreter.jump_switch_off(self.__switch_number)
            case "down":
                interpreter.jump_switch_down(self.__switch_number)
            case "up":
                interpreter.jump_switch_up(self.__switch_number)
            case _:
                message = "Switch can be set up, down, or sender, found: {0}.".format(setting)
                print(message)
        mask = interpreter.jump_set_mask()
        storage.set_jump_switch_mask(mask)
        return True

class Resume:
    """
    Resumes execution.
    """

    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        storage.run()
        return False

class SetA(Runner):
    """
    Sets the accumulator (i.e. A register)
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        value = self._to_int(0o0, 0o7777, setting)
        if 0 <= value:
            storage.a_register = value
        return True

class SetB(Runner):
    """
    Set the buffer control bank number
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        value = self._to_int(0, 0o7, setting)
        if 0 <= value:
            storage.buffer_storage_bank = value
        return True

class SetD(Runner):
    """
    Set the direct storage bank number
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        value = self._to_int(0o0, 0o7, setting)
        if 0 <= value:
            storage.direct_storage_bank = value
        return True

class SetI(Runner):
    """
    Set the indirect storage bank number
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        value = self._to_int(0o0, 0o7, setting)
        if 0 <= value:
            storage.indirect_storage_bank = value
        return True

class SetP(Runner):
    """
    Set the program address (i.e. P register)
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        value = self._to_int(0o0, 0o7777, setting)
        if 0 <= value:
            storage.p_register = value
        return True

class SetR(Runner):
    """
    Set the relative bank number
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        value = self._to_int(0o0, 0o7, setting)
        if 0 <= value:
            storage.relative_storage_bank = value
        return True

class Step(Runner):
    """
    Run the next instruction.
    """
    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        storage.stop()
        return False

class StopSwitch(Runner):
    """
    Set stop switches. Stop switches can be set up, down, or center (i.e. off)
    """
    def __init__(self, switch_number: int):
        self.__switch_number = switch_number

    def apply(self, interpreter: Interpreter, storage: Storage, setting: str) -> bool:
        match setting:
            case "center":
                interpreter.stop_switch_off(self.__switch_number)
            case "down":
                interpreter.stop_switch_down(self.__switch_number)
            case "up":
                interpreter.stop_switch_up(self.__switch_number)
            case _:
                print("Switch can be set center, down, or up, found {0}.".format(setting))
        mask = interpreter.stop_set_mask()
        storage.set_stop_switch_mask(mask)
        return True

# Available commands
COMMANDS: {str: Runner} = {
    "assemble": AssembleAndRunIfErrorFree(),
    "exit": Exit(),
    "halt": Step(),
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
