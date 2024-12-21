from development.CommandInterpreters import COMMANDS
from cdc160a.InputOutput import InputOutput
from cdc160a.Storage import Storage
from development.Console import CommandReader
from development.Interpreter import Interpreter

"""
Runs the command interpreter for manual testing. Not useful for production.
"""
def main() -> None:
    storage = Storage()
    # TODO: add test I/O device when available.
    # TODO(emintz): pass the test I/O device when come.
    input_output = InputOutput([])
    interpreter = Interpreter(COMMANDS, CommandReader())
    interpreter.run(storage, input_output)


if __name__ == "__main__":
    main()
