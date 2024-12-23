from unittest import TestCase
import os
from tempfile import NamedTemporaryFile

from cdc160a.InputOutput import InputOutput
from cdc160a.PaperTapeReader import PaperTapeReader
from test_support.HyperLoopQuantumGravityBiTape import HyperLoopQuantumGravityBiTape

_BI_TAPE_INPUT_DATA = [
    0o7777, 0o0001, 0o0200, 0o0210, 0o1111,
    0o4001, 0o4011, 0o4111, 0o4112, 0o4122]

class TestInputOutput(TestCase):
    def setUp(self) -> None:
        self.__bi_tape = HyperLoopQuantumGravityBiTape(_BI_TAPE_INPUT_DATA)
        self.__paper_tape_reader = PaperTapeReader()
        self.__input_output = InputOutput(
            [self.__paper_tape_reader, self.__bi_tape])

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

    def test_read_delay_no_device_selected(self) -> None:
        assert self.__input_output.read_delay() == 0

    def test_read_delay_bi_tape_selected(self) -> None:
        self.__bi_tape.set_online_status(True)
        device_status, valid_request =\
            self.__input_output.external_function(0o3700)
        assert device_status == 0o0001
        assert valid_request
        assert self.__input_output.read_delay() == 3

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

    def test_write_delay_no_device_selected(self) -> None:
        assert self.__input_output.write_delay() == 0

    def test_write_delay_bi_tape_selected(self) -> None:
        device_status, operation_succeeded = (
            self.__input_output.external_function(0o3700))
        assert operation_succeeded
        assert device_status == 0o4000
        assert self.__input_output.write_delay() == 4

    def test_write_no_device_selected(self) -> None:
        assert not self.__input_output.write_normal(0o4040)

    def test_write_device_selected_and_offline(self) -> None:
        device_status, operation_succeeded = (
            self.__input_output.external_function(0o3700))
        assert operation_succeeded
        assert device_status == 0o4000

        assert not self.__input_output.write_normal(0o4040)
        assert self.__bi_tape.output_data() == []

    def test_write_device_selected_and_ready(self) -> None:
        self.__bi_tape.set_online_status(True)
        device_status, operation_succeeded = (
            self.__input_output.external_function(0o3700))
        assert operation_succeeded
        assert device_status == 0o0001

        assert self.__input_output.write_normal(0o4040)
        assert self.__bi_tape.output_data() == [0o4040]
