from unittest import TestCase
import os
from tempfile import NamedTemporaryFile

from cdc160a.InputOutput import InputOutput
from cdc160a.PaperTapeReader import PaperTapeReader

class TestInputOutput(TestCase):
    def setUp(self) -> None:
        self.__paper_tape_reader = PaperTapeReader()
        self.__input_output = InputOutput([self.__paper_tape_reader])

    def test_select_no_device_accepts_code(self):
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None
        response, status = self.__input_output.external_function(0o5000)
        assert response is None
        assert not status
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None

    def test_select_device_offline(self) -> None:
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None
        response, status = self.__input_output.external_function(0o4102)
        assert response is None
        assert not status
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() is None

    def test_select_valid_device(self) -> None:
        temp_file = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(temp_file.name))
        temp_file.write("0\n7\n007\n456\n")
        temp_file.close()

        self.__paper_tape_reader.open(temp_file.name)

        response, status = self.__input_output.external_function(0o4102)
        self.__paper_tape_reader.close()
        os.unlink(temp_file.name)

        assert response is None
        assert status
        assert self.__input_output.device_on_buffer_channel() is None
        assert self.__input_output.device_on_normal_channel() == self.__paper_tape_reader

    def test_read_no_device_selected(self) -> None:
        status, value = self.__input_output.read_normal()
        assert not status
        assert value == 0

    def test_read_device_ready(self) -> None:
        temp_file = NamedTemporaryFile("w+", delete=False)
        print("Temporary file: {0},".format(temp_file.name))
        temp_file.write("456\n")
        temp_file.close()

        self.__paper_tape_reader.open(temp_file.name)

        self.__input_output.external_function(0o4102)
        status, value = self.__input_output.read_normal()
        assert status
        assert value == 0o456

        self.__paper_tape_reader.close()
        os.unlink(temp_file.name)
