"""
A bank of three switches
"""

from test_support.ConsoleSwitch import ConsoleSwitch

class SwitchBank:
    def __init__(self):
        self.__switches = [
            ConsoleSwitch(0),
            ConsoleSwitch(1),
            ConsoleSwitch(2)
        ]

    def any_down(self) -> bool:
        result = False
        for switch in self.__switches:
            result = result or switch.is_down()
        return result

    def mask(self) -> int:
        result = 0
        for switch in self.__switches:
            result |= switch.on_off_bit()
        return result

    def return_to_center(self, index: int) -> None:
        assert 0 <= index <= 3
        self.__switches[index].return_to_center()

    def set_down(self, index: int) -> None:
        assert 0 <= index <= 2
        self.__switches[index].set_down()

    def set_up(self, index: int) -> None:
        assert 0 <= index <= 2
        self.__switches[index].set_up()