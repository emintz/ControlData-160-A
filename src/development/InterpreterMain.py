from development.CommandInterpreters import COMMANDS
from cdc160a.Storage import Storage
from development.Console import CommandReader
from development.Interpreter import Interpreter

"""
Runs the command interpreter for manual testing. Not useful for production.
"""
def main() -> None:
    storage = Storage()
    interpreter = Interpreter(COMMANDS, CommandReader())
    interpreter.run(storage)


if __name__ == "__main__":
    main()
