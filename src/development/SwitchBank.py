"""
A bank of three switches
"""

from development.ConsoleSwitch import ConsoleSwitch, SwitchState


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

    def down_mask(self) -> int:
        result = 0
        for switch in self.__switches:
            if switch.is_down():
                result |= switch.on_off_bit()
        return result

    def mask(self) -> int:
        result = 0
        for switch in self.__switches:
            result |= switch.on_off_bit()
        return result

    def release_down_switches(self) -> None:
        for switch in self.__switches:
            switch.release_if_down()

    def return_to_center(self, index: int) -> None:
        assert 0 <= index <= 3
        self.__switches[index].return_to_center()

    def set_down(self, index: int) -> None:
        assert 0 <= index <= 2
        self.__switches[index].set_down()

    def set_up(self, index: int) -> None:
        assert 0 <= index <= 2
        self.__switches[index].set_up()

    def switch_state(self, index: int) -> SwitchState:
        assert 0 <= index <= 2
        return self.__switches[index].switch_state()

    def switch_state_name(self, index: int) -> str:
        assert 0 <= index <= 2
        return self.__switches[index].state_name()
