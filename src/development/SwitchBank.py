"""
Jump or stop switch bank

Copyright © 2025 The System Source Museum, the authors and maintainers,
and others

This file is part of the System Source Museum Control Data 160-A Emulator.

The System Source Museum Control Data 160-A Emulator is free software: you
can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

The System Source Museum Control Data 160-A Emulator is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with the System Source Museum Control Data 160-A Emulator. If not, see
<https://www.gnu.org/licenses/.
"""

from development.ConsoleSwitch import ConsoleSwitch, SwitchState

class SwitchBank:
    """
    A bank of three switches that can emulate a set of jump or
    stop switches.
    """

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
