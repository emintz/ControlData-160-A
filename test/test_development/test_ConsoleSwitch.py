from unittest import TestCase

from development.ConsoleSwitch import ConsoleSwitch
from development.ConsoleSwitch import SwitchState


class TestConsoleSwitch(TestCase):

    def setUp(self) -> None:
        self.__switch = ConsoleSwitch(1)

    def test_is_down(self):
        assert not self.__switch.is_down()
        assert self.__switch.switch_state() == SwitchState.CENTER
        assert self.__switch.state_name() == "center"
        self.__switch.set_up()
        assert not self.__switch.is_down()
        assert self.__switch.switch_state() == SwitchState.UP
        assert self.__switch.state_name() == "up"
        self.__switch.set_down()
        assert self.__switch.is_down()
        assert self.__switch.switch_state() == SwitchState.DOWN
        assert self.__switch.state_name() == "down"
        self.__switch.return_to_center()
        assert not self.__switch.is_down()
        assert self.__switch.switch_state() == SwitchState.CENTER
        assert self.__switch.state_name() == "center"

    def test_on_off_bit(self):
        assert self.__switch.on_off_bit() == 0
        assert self.__switch.switch_state() == SwitchState.CENTER
        self.__switch.set_up()
        assert self.__switch.on_off_bit() == 2
        self.__switch.return_to_center()
        assert self.__switch.on_off_bit() == 0
        self.__switch.set_down()
        assert self.__switch.on_off_bit() == 2
