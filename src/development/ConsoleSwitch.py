"""
Console switch hardware emulation

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


from enum import Enum

class SwitchState(Enum):
    """
    Switch states: up, centered, or down.
    """
    UP = 1
    CENTER = 2
    DOWN = 3

STATE_NAMES = {
    SwitchState.CENTER: "center",
    SwitchState.DOWN: "down",
    SwitchState.UP: "up",
}

class ConsoleSwitch:
    """
    Emulates a console switch. Switches can be up, centered (off), or down.
    Each switch has a value of a non-negative power of two when on (up or
    down), or zero when off to support masking. See the SwitchBank class
    for details. Note that this class is used to emulate both jump and
    stop switches.
    """
    def __init__(self, bit_no: int):
        """
        Constructor. Switches are created in the CENTER (off) state.

        :param bit_no: a non-negative bit (a.k.a. power of two) number
        """
        self.__bit = 1 << bit_no
        self.__state = SwitchState.CENTER

    def is_down(self) -> bool:
        """
        Test if this switch is down

        :return: True if and only if this switch is down.
        """
        return self.__state == SwitchState.DOWN

    def on_off_bit(self) -> int:
        """
        Returns this switch's on/off state.

        :return: 0 if this switch is centered (off), otherwise the
                 switch's power of two value
        """
        return 0 if self.__state == SwitchState.CENTER else self.__bit

    def release_if_down(self) -> None:
        if self.__state == SwitchState.DOWN:
            self.__state = SwitchState.CENTER

    def return_to_center(self) -> None:
        """
        Returns this switch to the center position.

        :return: None
        """
        self.__state = SwitchState.CENTER

    def set_down(self) -> None:
        """
        Sets this switch to the UP position.

        :return: None
        """
        self.__state = SwitchState.DOWN

    def set_up(self) -> None:
        """
        Sets this switch to the DOWN position.

        :return: None
        """
        self.__state = SwitchState.UP

    def switch_state(self) -> SwitchState:
        return self.__state

    def state_name(self) -> str:
        return STATE_NAMES[self.__state]
