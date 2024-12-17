from unittest import TestCase
import os

from cdc160a.Device import ExternalFunctionAction
from tempfile import NamedTemporaryFile
from PaperTapeReader import PaperTapeReader

class TestPaperTapeReader(TestCase):


    def setUp(self) -> None:
        self.__paper_tape_reader = PaperTapeReader()

    def test_accepts(self) -> None:
        assert self.__paper_tape_reader.accepts(0o4102)
        assert  not self.__paper_tape_reader.accepts(0o4101)
        assert  not self.__paper_tape_reader.accepts(0o4103)
        assert  not self.__paper_tape_reader.accepts(0o4104)

    def test_close_when_not_open(self) -> None:
        """
        Test succeeds if it does not crash.

        :return: None
        """
        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()

    def test_open_invalid_input_close(self) -> None:
        tempfile = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(tempfile.name))
        tempfile.write("0\n7\n007\ngorp\n456\n")
        tempfile.close()
        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.open(tempfile.name)
        assert self.__paper_tape_reader.is_open()
        assert (self.__paper_tape_reader.name() ==
                tempfile.name)
        assert self.__paper_tape_reader.read() == 0
        assert self.__paper_tape_reader.read() == 0o7
        assert self.__paper_tape_reader.read() == 0o7
        assert self.__paper_tape_reader.read() == 0
        assert self.__paper_tape_reader.read() == 0o456
        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()
        os.unlink(tempfile.name)
        assert not os.path.exists(tempfile.name)

    def test_open_valid_input_close(self) -> None:
        tempfile = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(tempfile.name))
        tempfile.write("0\n7\n007\n456\n")
        tempfile.close()
        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.open(tempfile.name)
        assert self.__paper_tape_reader.is_open()
        assert (self.__paper_tape_reader.name() ==
                tempfile.name)
        assert self.__paper_tape_reader.read() == 0
        assert self.__paper_tape_reader.read() == 0o7
        assert self.__paper_tape_reader.read() == 0o7
        assert self.__paper_tape_reader.read() == 0o456
        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()
        os.unlink(tempfile.name)
        assert not os.path.exists(tempfile.name)

    def test_read_delay(self) -> None:
        assert self.__paper_tape_reader.read_delay() == 446

    def test_valid_external_function(self) -> None:
        (function_action, status) = self.__paper_tape_reader.external_function(
            0o4102)
        assert function_action == ExternalFunctionAction.NORMAL_SELECT
        assert status is None
