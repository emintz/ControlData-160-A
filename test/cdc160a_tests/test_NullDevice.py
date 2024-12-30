from unittest import TestCase
from NullDevice import NullDevice


class TestNullDevice(TestCase):
    def setUp(self) -> None:
        self.__null_device = NullDevice()

    def test_accepts(self) -> None:
        assert self.__null_device.accepts(0o7777)
        assert not self.__null_device.accepts(0o3700)
        assert not self.__null_device.accepts(0o4102)
        assert not self.__null_device.accepts(0o4104)

    def test_external_function(self) -> None:
        valid_request, status = self.__null_device.external_function(0o7777)
        assert valid_request
        assert status == 0o0000
        valid_request, status = self.__null_device.external_function(0o0000)
        assert not valid_request
        assert status == 0o0000

    def test_initial_read_delay(self) -> None:
        assert self.__null_device.initial_write_delay() == 1

    def test_initial_write_delay(self) -> None:
        assert self.__null_device.initial_write_delay() == 1

    def test_open_and_close(self) -> None:
        assert self.__null_device.file_name() is None
        assert not self.__null_device.is_open()
        assert self.__null_device.open("Ipcress")
        assert self.__null_device.is_open()
        assert self.__null_device.file_name() == "Ipcress"
        self.__null_device.close()
        assert self.__null_device.file_name() is None
        assert not self.__null_device.is_open()

    def test_read(self) -> None:
        valid_request, value = self.__null_device.read()
        assert valid_request
        assert value == 0

    def test_read_delay(self) -> None:
        assert self.__null_device.read_delay() == 1

    def test_write(self) -> None:
        assert self.__null_device.write(0o1234)

    def test_write_delay(self) -> None:
        assert self.__null_device.write_delay() == 1
