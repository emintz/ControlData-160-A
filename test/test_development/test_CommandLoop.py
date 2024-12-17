import unittest
from unittest import TestCase
from cdc160a.Storage import Storage
from development import CommandInterpreters
from development import Interpreter

class CommandReaderForTesting:
    def __init__(self):
        self.tokens = [""]

    def read_command(self) -> [str]:
        return self.tokens

class TestInterpreter(TestCase):

    def setUp(self) -> None:
        self.__command_reader = CommandReaderForTesting()
        self.__storage = Storage()
        self.__interpreter = Interpreter.Interpreter(CommandInterpreters.COMMANDS, self.__command_reader)


if __name__ == "__main__":
    unittest.main()
