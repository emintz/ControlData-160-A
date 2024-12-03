from venv import create

from cdc160a.Storage import Storage
from system_specific import Factory
from typing import Callable

from development import CommandInterpreters
from development.Interpreter import Interpreter

class Console:
    """
    A command line driven console, a stopgap for use until a full-fledged
    GUI becomes available. This console takes command from the terminal.
    """

    def __init__(
            self,
            input_checker: Callable[[], bool],
            interpreter: Interpreter):
        self.__input_checker = input_checker
        self.__interpreter = interpreter

    def before_instruction_fetch(self, storage: Storage) -> None:
        """
        Performs console-related tasks required to fetch an instruction.

        The run loop invokes this method just before it fetches an instruction.
        Implementations should set the jump and stop switch masks in the
        provided Storage.

        :param storage: memory and register file
        :return: None
        """
        if not storage.run_stop_status or self.__input_checker():
            self.__interpreter.run(storage)
        pass

    def before_instruction_logic(self, storage: Storage) -> None:
        """
        Perform console-related tasks required to run instruction logic.

        The run loop invokes this method after it unpacks the instruction
        and determines its effective address. Implementations should halt
        the machine if the user has moved the run/stop switch to stop.

        :param storage: memory and register file
        :return: None
        """
        pass

    def before_advance(self, storage: Storage) -> bool:
        """
        Perform module-related tasks required to advance to the next
        instruction. Implementations should stop and display the console
        if the machine has been halted by HLT, ERR, or for any other reasons.

        To support testing, the run loop will halt when this method
        returns False. Production implementations must always return True.

        :param storage: memory and register file
        :return: True if the run loop should keep going, False if the run
                 loop should exit. This is to support PyUnit testing.
                 Production versions must return True.
        """
        return True



class CommandReader:
    """
    Reads commands from the keyboard
    """
    def read_command(self) -> [str]:
        command = input("> ")
        return command.split()

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
    while True:
        console.before_instruction_fetch(storage)
        console.before_instruction_logic(storage)
        console.before_advance(storage)

if __name__ == "__main__":
    main()
