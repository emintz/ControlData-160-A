from unittest import TestCase
import os

from cdc160a.Device import IOChannelSupport
from cdc160a.PaperTapeReader import PaperTapeReader
from tempfile import NamedTemporaryFile

class TestPaperTapeReader(TestCase):

    def setUp(self) -> None:
        self.__paper_tape_reader = PaperTapeReader()

    @staticmethod
    def _create_temp_file(contents: str) -> str:
        with NamedTemporaryFile("w+", delete=False) as temp_file:
            file_name = temp_file.name
            print("Temporary file: {0},".format(temp_file.name))
            temp_file.write(contents)
        return file_name

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

    def test_configuration(self) -> None:
        assert self.__paper_tape_reader.can_read()
        assert not self.__paper_tape_reader.can_write()
        io_channel_support = self.__paper_tape_reader.io_channel_support()
        assert io_channel_support == IOChannelSupport.NORMAL_ONLY

    def test_open_invalid_input_close(self) -> None:
        temp_file_name = self._create_temp_file("0\n7\n007\ngorp\n456\n")
        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.open(temp_file_name)
        assert self.__paper_tape_reader.is_open()
        assert (self.__paper_tape_reader.file_name() ==
                temp_file_name)
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0o7
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0o7
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0o456
        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()
        os.unlink(temp_file_name)
        assert not os.path.exists(temp_file_name)

    def test_open_valid_input_close(self) -> None:
        temp_file_name = self._create_temp_file("0\n7\n007\n456\n")
        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.open(temp_file_name)
        assert self.__paper_tape_reader.is_open()
        assert self.__paper_tape_reader.file_name() == temp_file_name
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0o7
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0o7
        read_status, data = self.__paper_tape_reader.read()
        assert read_status
        assert data == 0o456
        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()
        os.unlink(temp_file_name)
        assert not os.path.exists(temp_file_name)

    def test_read_delay(self) -> None:
        assert self.__paper_tape_reader.read_delay() == 446

    def test_valid_external_function_tape_mounted(self) -> None:
        temp_file_name = self._create_temp_file("0\n7\n007\n456\n")

        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.open(temp_file_name)

        (valid_request, status) = self.__paper_tape_reader.external_function(
            0o4102)
        assert valid_request
        assert status is None

        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()
        os.unlink(temp_file_name)
        assert not os.path.exists(temp_file_name)

    def test_valid_external_function_no_tape_mounted(self) -> None:
        (valid_request, status) = self.__paper_tape_reader.external_function(
            0o4102)
        assert not valid_request
        assert status is None

    def test_invalid__external_function_tape_mounted(self) -> None:
        temp_file_name = self._create_temp_file("0\n7\n007\n456\n")

        assert not self.__paper_tape_reader.is_open()
        self.__paper_tape_reader.open(temp_file_name)

        (valid_request, status) = self.__paper_tape_reader.external_function(
            0o4100)
        assert not valid_request
        assert status is None

        self.__paper_tape_reader.close()
        assert not self.__paper_tape_reader.is_open()
        os.unlink(temp_file_name)
        assert not os.path.exists(temp_file_name)
