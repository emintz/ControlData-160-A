from unittest import TestCase

from test_support.ConsoleSwitch import ConsoleSwitch


class TestConsoleSwitch(TestCase):

    def setUp(self) -> None:
        self.__switch = ConsoleSwitch(1)

    def test_is_down(self):
        assert not self.__switch.is_down()
        self.__switch.set_up()
        assert not self.__switch.is_down()
        self.__switch.set_down()
        assert self.__switch.is_down()
        self.__switch.return_to_center()
        assert not self.__switch.is_down()

    def test_on_off_bit(self):
        assert self.__switch.on_off_bit() == 0
        self.__switch.set_up()
        assert self.__switch.on_off_bit() == 2
        self.__switch.return_to_center()
        assert self.__switch.on_off_bit() == 0
        self.__switch.set_down()
        assert self.__switch.on_off_bit() == 2
